from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2, jwt, configparser
import os, json, datetime
from functools import wraps

app = Flask(__name__)
cors = CORS(app, origins="*")


def read_config(file_name="config.ini"):
    # 获取当前运行脚本的路径
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, file_name)

    # 初始化ConfigParser并读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    # 用于加密 JWT 的密钥
    app.config["SECRET_KEY"] = config["SECRET_KEY"]["SECRET_KEY"]

    # 从配置文件中获取数据库连接参数
    db_params = {
        "dbname": config["DATABASE"]["DB_NAME"],
        "user": config["DATABASE"]["DB_USER"],
        "password": config["DATABASE"]["DB_PASSWORD"],
        "host": config["DATABASE"]["DB_HOST"],
        "port": config["DATABASE"]["DB_PORT"],
    }
    return db_params


# 数据库连接参数
db_params = read_config()


# 修饰器函数：连接数据库
def connect_db(func):
    def wrapper(*args, **kwargs):
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        try:
            # 将连接和游标作为参数传递给被修饰的函数
            result = func(cursor, *args, **kwargs)
            connection.commit()
            return result
        except Exception as e:
            # 在异常情况下回滚事务
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    return wrapper


# 身份令牌生成函数
def generate_token(username):
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode(
        {"username": username, "exp": expiration_date},
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return token


# 身份令牌验证装饰器
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = data["username"]  # 提取用户名信息
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return func(xh=current_user, *args, **kwargs)

    return decorated


@token_required
@connect_db
def enroll_student(cursor, xh, kch, jsgh):
    # 在 E 表中插入选课信息
    insert_query = """
        INSERT INTO E (xh, kch, jsgh)
        VALUES (%(xh)s, %(kch)s, %(jsgh)s);
    """

    parameters = {
        "xh": xh,
        "kch": kch,
        "jsgh": jsgh,
    }

    # 执行插入操作
    cursor.execute(insert_query, parameters)
    return jsonify({"status": "success"})


@connect_db
def get_partial_schedule(
    cursor,
    start_position,
    length=20,
    kch=None,
    kcm=None,
    xf=None,
    jsh=None,
    jsxm=None,
    sksj=None,
):
    # 构建 SQL 查询总数的语句
    count_query = """
        SELECT
            COUNT(*)
        FROM
            O
        JOIN
            C ON O.kch = C.kch
        JOIN
            T ON O.jsgh = T.jsgh
    """

    # 添加约束条件
    where_conditions = []
    parameters = {}

    if kch is not None:
        where_conditions.append("O.kch = %(kch)s")
        parameters["kch"] = kch
    if kcm is not None:
        where_conditions.append("C.kcm = %(kcm)s")
        parameters["kcm"] = kcm
    if xf is not None:
        where_conditions.append("C.xf = %(xf)s")
        parameters["xf"] = xf
    if jsh is not None:
        where_conditions.append("O.jsh = %(jsh)s")
        parameters["jsh"] = jsh
    if jsxm is not None:
        where_conditions.append("T.jsxm = %(jsxm)s")
        parameters["jsxm"] = jsxm
    if sksj is not None:
        where_conditions.append("O.sksj = %(sksj)s")
        parameters["sksj"] = sksj

    if where_conditions:
        count_query += " WHERE " + " AND ".join(where_conditions)

    # 执行总数查询
    cursor.execute(count_query, parameters)
    total_count = cursor.fetchone()[0]

    # 构建 SQL 查询分页的语句
    schedule_query = """
        SELECT
            O.kch,
            C.kcm,
            O.jsh,
            T.jsxm,
            O.sksj,
            C.xf,
            C.zdrs
        FROM
            O
        JOIN
            C ON O.kch = C.kch
        JOIN
            T ON O.jsgh = T.jsgh
    """

    if where_conditions:
        schedule_query += " WHERE " + " AND ".join(where_conditions)

    # 添加排序和分页
    schedule_query += f"""
        ORDER BY
            O.kch
        OFFSET
            %(start_position)s
        LIMIT
            %(length)s;
    """
    parameters["start_position"] = start_position
    parameters["length"] = length

    # 执行分页查询
    cursor.execute(schedule_query, parameters)
    rows = cursor.fetchall()
    partial_schedule = [
        {
            "kch": row[0],
            "kcm": row[1],
            "jsh": row[2],
            "jsxm": row[3],
            "sksj": row[4],
            "xf": row[5],
            "zdrs": row[6],
        }
        for row in rows
    ]

    # 将总数和分页结果一起返回
    return jsonify(
        {
            "total_count": total_count,
            "course_info": partial_schedule,
            "status": "success",
        }
    )


# 用户登录
@app.route("/login/", methods=["GET", "POST"], endpoint="/login/")
@connect_db
def login(cursor):
    data = json.loads(request.get_data(as_text=True))
    print(data)
    # 在此实现登录功能，使用 cursor 进行数据库操作
    cursor.execute(f"SELECT P.mm FROM P WHERE P.xh = {data['login_info']['username']}")
    rows = cursor.fetchall()
    if len(rows) > 0 and rows[0][0].strip() == data["login_info"]["password"]:
        return jsonify(
            {
                "status": "success",
                "token": generate_token(data["login_info"]["username"]),
            }
        )
    else:
        return jsonify({"status": "failed"})


# 学生用户接口
@app.route("/enroll_course/", methods=["GET", "POST"], endpoint="/enroll_course/")
def enroll_course(cursor):
    # 获取前端发送的 JSON 表单
    data = request.get_json()

    # 判断是课程查询请求还是选课请求
    if "action" not in data["course_info"]:
        return jsonify({"status": "failed", "message": "Invalid request format"})

    action = data["action"]

    if action == "get_schedule":
        # 课程查询请求
        partial_schedule = get_partial_schedule(
            cursor,
            start_position=0,
            kch=data["kch"],
            kcm=data["kcm"],
            xf=data["xf"],
            jsh=data["jsh"],
            jsxm=data["jsxm"],
            sksj=data["sksj"],
        )
        return partial_schedule

    elif action == "enroll":
        # 选课请求
        response = enroll_student(
            cursor, data["course_info"]["kch"], data["course_info"]["jsgh"]
        )
        return response

    return jsonify({"status": "failed", "message": "Invalid action"})


@connect_db
def drop_course(cursor):
    # 在此实现退课功能，使用 cursor 进行数据库操作
    pass


@connect_db
def get_schedule(cursor):
    # 在此实现课表查询功能，使用 cursor 进行数据库操作
    pass


"""
查询可选课程
-- 查询学生可以选择的课程
SELECT C.kch, C.kcm, C.xf, C.zdrs
FROM C
LEFT JOIN E ON C.kch = E.kch
WHERE E.xh IS NULL;
"""


# 教师用户接口
@app.route("/teacher_schedule/", methods=["GET", "POST"], endpoint="/teacher_schedule/")
@connect_db
def get_teacher_schedule(cursor):
    # 在此实现教师课表查询功能，使用 cursor 进行数据库操作
    pass


# 管理员用户接口
@connect_db
def manage_course(cursor):
    # 在此实现增删查改课程功能，包括课程容量和锁课，使用 cursor 进行数据库操作
    pass


@connect_db
def manage_student(cursor):
    # 在此实现增删查改学生功能，使用 cursor 进行数据库操作
    pass


@connect_db
def manage_student_course(cursor):
    # 在此实现增删查改学生选择课程功能，使用 cursor 进行数据库操作
    pass


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001, threaded=True)
    # token = generate_token("test")
    # print(token)
    # manage_student_course()
