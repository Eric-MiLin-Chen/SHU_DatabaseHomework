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
def _enroll_student(cursor, xh, kch, jsgh):
    try:
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
    except psycopg2.errors.UniqueViolation:
        # 唯一性冲突，返回错误表单
        return jsonify({"status": "failed", "message": "UniqueViolation"})


@token_required
@connect_db
def _drop_course(cursor, xh, kch, jsgh):
    try:
        # 在 E 表中删除退课信息
        delete_query = """
            DELETE FROM E
            WHERE xh = %(xh)s AND kch = %(kch)s AND jsgh = %(jsgh)s;
        """

        parameters = {
            "xh": xh,
            "kch": kch,
            "jsgh": jsgh,
        }

        # 执行插入操作
        cursor.execute(delete_query, parameters)
        # 检查受影响的行数
        if cursor.rowcount == 0:
            # 没有匹配的记录，抛出自定义异常或返回错误信息
            raise Exception("No matching record found for deletion")

        # 返回 JSON 响应
        response = jsonify({"status": "success"})
        return response
    except psycopg2.errors.UniqueViolation:
        # 唯一性冲突，返回错误表单
        return jsonify({"status": "failed", "message": "UniqueViolation"})
    except Exception as e:
        # 处理其他异常，返回错误信息
        return jsonify({"status": "failed", "message": str(e)})


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


# 查询已选课程信息
@token_required
@connect_db
def get_enrolled_courses(cursor, xh):
    query = """
        SELECT
            E.kch,
            C.kcm,
            T.jsxm,
            O.sksj,
            C.xf
        FROM
            E
        JOIN
            C ON E.kch = C.kch
        JOIN
            T ON E.jsgh = T.jsgh
        JOIN
            O ON E.kch = O.kch
        WHERE
            E.xh = %(xh)s;
    """

    parameters = {"xh": xh}

    cursor.execute(query, parameters)
    rows = cursor.fetchall()

    enrolled_courses = [
        {
            "kch": row[0],
            "kcm": row[1],
            "jsxm": row[2],
            "sksj": row[3],
            "xf": row[4],
        }
        for row in rows
    ]

    return jsonify(enrolled_courses)


# @connect_db
# def get_teacher_schedule(jsgh):
#     query = """
#         SELECT
#             C.kch,
#             C.kcm,
#             O.sksj,
#             E.xh AS student_id,
#             S.xm AS student_name
#         FROM
#             O
#         JOIN
#             C ON O.kch = C.kch
#         LEFT JOIN
#             E ON O.kch = E.kch
#         LEFT JOIN
#             S ON E.xh = S.xh
#         WHERE
#             O.jsgh = %(jsgh)s;
#     """

#     parameters = {"jsgh": jsgh}

#     cursor.execute(query, parameters)
#     rows = cursor.fetchall()

#     teacher_schedule = {}
#     for row in rows:
#         kch, kcm, sksj, student_id, student_name = row
#         if kch not in teacher_schedule:
#             teacher_schedule[kch] = {
#                 "kch": kch,
#                 "kcm": kcm,
#                 "sksj": sksj,
#                 "student_info": [],
#             }
#         teacher_schedule[kch]["student_info"].append(
#             {"xh": student_id, "xm": student_name}
#         )

#     return jsonify(
#         {
#             "total_courses": len(teacher_schedule),
#             "courses": list(teacher_schedule.values()),
#         }
#     )


# 用户登录
@app.route("/login/", methods=["GET", "POST"], endpoint="/login/")
@connect_db
def login(cursor):
    try:
        data = request.get_json()
        print(data)
        xh = data["login_info"]["username"]
        password = data["login_info"]["password"]

        # 使用参数化查询，避免 SQL 注入攻击
        query = "SELECT P.mm FROM P WHERE P.xh = %s"
        cursor.execute(query, (xh,))

        rows = cursor.fetchall()
        if len(rows) > 0 and rows[0][0].strip() == password:
            return jsonify(
                {
                    "status": "success",
                    "Authorization": generate_token(xh),
                }
            )
        else:
            return jsonify({"status": "failed"})
    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})


# 学生用户接口
@app.route("/student_enroll/", methods=["GET", "POST"], endpoint="/student_enroll/")
def student_enroll():
    # 获取前端发送的 JSON 表单
    data = request.get_json()

    # 判断是课程查询请求还是选课请求
    if "action" not in data:
        return jsonify({"status": "failed", "message": "Invalid request format"})

    action = data["action"]

    if action == "get_schedule":
        # 课程查询请求
        partial_schedule = get_partial_schedule(
            start_position=0,
            kch=data["course_info"]["kch"],
            kcm=data["course_info"]["kcm"],
            xf=data["course_info"]["xf"],
            jsh=data["course_info"]["jsh"],
            jsxm=data["course_info"]["jsxm"],
            sksj=data["course_info"]["sksj"],
        )
        return partial_schedule

    elif action == "enroll":
        # 选课请求
        response = _enroll_student(
            data["course_info"]["kch"], data["course_info"]["jsgh"]
        )
        return response

    return jsonify({"status": "failed", "message": "Invalid action"})


# 退课功能
@app.route("/drop_course/", methods=["GET", "POST"], endpoint="/drop_course/")
def drop_course():
    # 获取前端发送的 JSON 表单
    data = request.get_json()

    # 判断是课程查询请求还是选课请求
    if "action" not in data:
        return jsonify({"status": "failed", "message": "Invalid request format"})

    action = data["action"]

    if action == "get_schedule":
        # 课程查询请求
        enrolled_courses = get_enrolled_courses()
        return jsonify(
            {"total_count": len(enrolled_courses), "course_info": enrolled_courses}
        )

    elif action == "drop":
        # 选课请求
        response = _drop_course(
            data["course_info"]["kch"],
            data["course_info"]["jsgh"],
        )
        return response

    return jsonify({"status": "failed", "message": "Invalid action"})


@app.route("/get_schedule/", methods=["GET", "POST"], endpoint="/get_schedule/")
def get_schedule():
    # 调用已有的函数获取已选课程信息
    enrolled_courses = get_enrolled_courses()

    # 返回已选课程信息的 JSON 响应
    return jsonify({"enrolled_courses": enrolled_courses})


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
