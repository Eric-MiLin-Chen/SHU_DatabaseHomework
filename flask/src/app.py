from flask import Flask, request, jsonify
from config_manager import ConfigManager
from db_manager import DBManager
from auth_manager import AuthManager
from student_manager import StudentManager
import psycopg2

app = Flask(__name__)

# 配置和数据库管理
config_manager = ConfigManager()
db_params = config_manager.get_db_params()
app.config["SECRET_KEY"] = config_manager.get_secret_key()

# 初始化管理器
db_manager = DBManager(db_params)
auth_manager = AuthManager(app.config["SECRET_KEY"])
student_manager = StudentManager(db_manager)


# 登录路由
@app.route("/login/", methods=["POST"])
@db_manager.connect_db
def login(cursor):
    data = request.get_json()
    print(data)
    username = data["login_info"]["username"]
    password = data["login_info"]["password"]

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    try:
        query = "SELECT P.mm FROM P WHERE P.xh = %s"
        cursor.execute(query, (username,))
        rows = cursor.fetchall()
        if len(rows) > 0 and rows[0][0].strip() == password:
            return jsonify(
                {
                    "status": "success",
                    "Authorization": auth_manager.generate_token(username),
                }
            )
        else:
            return jsonify({"status": "failed", "message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# 学生选课路由
@app.route("/student_enroll/", methods=["POST"])
@auth_manager.token_required
@db_manager.connect_db
def student_enroll(current_user):
    data = request.get_json()
    xh = current_user
    kch = data["course_info"]["kch"]
    jsgh = data["course_info"]["jsgh"]

    if not kch or not jsgh:
        return jsonify({"message": "Missing course ID or teacher ID"}), 400

    try:
        response = student_manager.enroll_student(xh, kch, jsgh)
        return response
    except psycopg2.errors.UniqueViolation:
        return jsonify({"message": "Already enrolled in this course"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# 学生退课路由
@app.route("/drop_course/", methods=["POST"])
@auth_manager.token_required
@db_manager.connect_db
def drop_course(cursor, current_user):
    data = request.get_json()
    xh = current_user  # 当前登录的学生学号
    kch = data["course_info"]["kch"]  # 课程号
    jsgh = data["course_info"]["jsgh"]  # 教师号

    if not kch or not jsgh:
        return jsonify({"message": "Missing course ID or teacher ID"}), 400

    try:
        response = student_manager.drop_course(cursor, xh, kch, jsgh)
        return response
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/get_schedule/", methods=["GET", "POST"], endpoint="/get_schedule/")
@auth_manager.token_required
@db_manager.connect_db
def get_schedule(cursor, current_user):
    xh = current_user
    # 调用已有的函数获取已选课程信息
    enrolled_courses = student_manager.get_enrolled_courses(cursor, xh)

    # 返回已选课程信息的 JSON 响应
    return jsonify({"enrolled_courses": enrolled_courses})


# 教师用户接口
@app.route("/teacher_schedule/", methods=["GET", "POST"], endpoint="/teacher_schedule/")
@auth_manager.token_required
@db_manager.connect_db
def get_teacher_schedule(cursor, current_user):
    # 在此实现教师课表查询功能，使用 cursor 进行数据库操作
    pass


# 管理员用户接口
@app.route("/manage_course/", methods=["GET", "POST"], endpoint="/manage_course/")
@auth_manager.token_required
@db_manager.connect_db
def manage_course(cursor, current_user):
    # 在此实现增删查改课程功能，包括课程容量和锁课，使用 cursor 进行数据库操作
    pass


@app.route("/manage_student/", methods=["GET", "POST"], endpoint="/manage_course/")
@auth_manager.token_required
@db_manager.connect_db
def manage_student(cursor, current_user):
    # 在此实现增删查改学生功能，使用 cursor 进行数据库操作
    pass


@app.route(
    "/manage_student_course/", methods=["GET", "POST"], endpoint="/manage_course/"
)
@auth_manager.token_required
@db_manager.connect_db
def manage_student_course(cursor, current_user):
    # 在此实现增删查改学生选择课程功能，使用 cursor 进行数据库操作
    pass


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)
