from flask import Flask, request, jsonify
from flask_cors import CORS
from config_manager import ConfigManager
from db_manager import DBManager
from auth_manager import AuthManager
from user_manager import UserManager

app = Flask(__name__)
cors = CORS(app, origins="*")

# 配置和数据库管理
config_manager = ConfigManager()
db_params = config_manager.get_db_params()
app.config["SECRET_KEY"] = config_manager.get_secret_key()

# 初始化管理器
db_manager = DBManager(db_params)
auth_manager = AuthManager(app.config["SECRET_KEY"])
user_manager = UserManager(db_manager, auth_manager)


# 登录路由
@app.route("/login/", methods=["POST"])
@db_manager.connect_db
def login(cursor):
    data = request.get_json()
    username = data["login_info"]["username"]
    password = data["login_info"]["password"]
    if not username or not password:
        return (
            jsonify({"status": "failed", "message": "Missing username or password"}),
            400,
        )

    try:
        user_type = user_manager.verify_credentials(cursor, username, password)
        if user_type is not None:
            user_info = user_manager.get_user_info(cursor, user_type, username)
            ans = {
                "Authorization": auth_manager.generate_token(
                    username, user_info["user_info"]["role"]
                ),
                **user_info,
            }
            return jsonify(
                {
                    "Authorization": auth_manager.generate_token(
                        username, user_info["user_info"]["role"]
                    ),
                    **user_info,
                }
            )
        else:
            return jsonify({"status": "failed", "message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)}), 500


# 学生选课路由
@app.route("/student_enroll/", methods=["POST"], endpoint="/student_enroll/s")
@auth_manager.token_required("student")
@db_manager.connect_db
def student_enroll(cursor, current_user):
    # 获取前端发送的 JSON 表单
    data = request.get_json()
    print(data)
    xh = current_user

    # 判断是课程查询请求还是选课请求
    if "action" not in data:
        return jsonify({"status": "failed", "message": "Invalid request format"})

    action = data["action"]

    if action == "get_schedule":
        # 课程查询请求
        partial_schedule = user_manager.get_partial_schedule(
            cursor=cursor,
            start_position=0,
            length=20,
            kch=data["course_info"]["kch"],
            kcm=data["course_info"]["kcm"],
            xf=data["course_info"]["xf"],
            jsh=data["course_info"]["jsh"],
            jsxm=data["course_info"]["jsxm"],
            sksj=data["course_info"]["sksj"],
        )
        print(partial_schedule)
        return partial_schedule

    elif action == "enroll":
        # 选课请求
        response = user_manager.enroll_student(
            cursor,
            xh=xh,
            kch=data["course_info"]["kch"],
            jsh=data["course_info"]["jsh"],
        )
        return response

    return jsonify({"status": "failed", "message": "Invalid action"})


# 学生退课路由
@app.route("/drop_course/", methods=["POST"], endpoint="/drop_course/")
@auth_manager.token_required("student")
@db_manager.connect_db
def drop_course(cursor, current_user):
    data = request.get_json()
    xh = current_user  # 当前登录的学生学号

    # 判断是课程查询请求还是选课请求
    if "action" not in data:
        return jsonify({"status": "failed", "message": "Invalid request format"})

    action = data["action"]

    if action == "get_schedule":
        # 课程查询请求
        enrolled_courses = user_manager.get_enrolled_courses(cursor=cursor, xh=xh)
        return jsonify(
            {
                "status": "success",
                "total_count": len(enrolled_courses),
                "course_info": enrolled_courses,
            }
        )

    elif action == "drop":
        # 选课请求
        response = user_manager.drop_course(
            cursor=cursor,
            xh=xh,
            kch=data["course_info"]["kch"],
            jsh=data["course_info"]["jsh"],
        )
        return response

    return jsonify({"status": "failed", "message": "Invalid action"})


@app.route("/get_schedule/", methods=["GET", "POST"], endpoint="/get_schedule/")
@auth_manager.token_required("student")
@db_manager.connect_db
def get_schedule(cursor, current_user):
    data = request.get_json()
    xh = current_user
    if "action" not in data:
        return jsonify({"status": "failed", "message": "Invalid request format"})

    action = data["action"]

    if action == "get_schedule":
        # 调用已有的函数获取已选课程信息
        enrolled_courses = user_manager.get_enrolled_courses(cursor, xh)

        # 返回已选课程信息的 JSON 响应
        return jsonify(
            {
                "status": "success",
                "total_count": len(enrolled_courses),
                "course_info": enrolled_courses,
            }
        )
    return jsonify({"status": "failed", "message": "Invalid action"})


# 教师用户接口
@app.route("/teacher_schedule/", methods=["GET", "POST"], endpoint="/teacher_schedule/")
@auth_manager.token_required("teacher")
@db_manager.connect_db
def get_teacher_schedule(cursor, current_user):
    data = request.get_json()
    jsgh = current_user
    if "action" not in data:
        return jsonify({"status": "failed", "message": "Invalid request format"})

    action = data["action"]

    # 调用已有的函数获取已选课程信息
    enrolled_courses = user_manager.get_teacher_schedule(cursor, jsgh)

    # 返回已选课程信息的 JSON 响应
    return jsonify(enrolled_courses)


# 管理员用户接口
@app.route("/manage_course/", methods=["GET", "POST"], endpoint="/manage_course/")
@auth_manager.token_required("admin")
@db_manager.connect_db
def manage_course(cursor, current_user):
    pass


@app.route("/manage_student/", methods=["GET", "POST"], endpoint="/manage_student/")
@auth_manager.token_required("admin")
@db_manager.connect_db
def manage_student(cursor, current_user):
    # 在此实现增删查改学生功能，使用 cursor 进行数据库操作
    pass


@app.route(
    "/manage_student_course/",
    methods=["GET", "POST"],
    endpoint="/manage_student_course/",
)
@auth_manager.token_required("admin")
@db_manager.connect_db
def manage_student_course(cursor, current_user):
    # 在此实现增删查改学生选择课程功能，使用 cursor 进行数据库操作
    pass


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)
