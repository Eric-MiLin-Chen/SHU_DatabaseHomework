from flask import jsonify
import psycopg2


class UserManager:
    def __init__(self, db_manager, auth_manager):
        self.db_manager = db_manager
        self.auth_manager = auth_manager

    def verify_credentials(self, cursor, username, password):
        """验证用户凭据并返回用户类型"""
        query = "SELECT mm, qx FROM P WHERE xh = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result and result[0].strip() == password:
            return result[1]  # 返回用户类型
        return None

    def get_user_info(self, cursor, user_type, username):
        """根据用户类型获取用户信息"""
        if user_type == "0":
            return self.__get_admin_info(cursor, username, user_type)

        elif user_type == "1":
            return self.__get_teacher_info(cursor, username, user_type)

        elif user_type == "2":
            return self.__get_student_info(cursor, username, user_type)

        return {}

    def __get_student_info(self, cursor, username, user_type):
        """获取学生信息"""
        student_query = "SELECT xh, xm, yxh, nj, xb FROM S WHERE xh = %s"
        cursor.execute(student_query, (username,))
        user_info = cursor.fetchone()
        return {
            "user_info": {
                "username": user_info[0],
                "name": user_info[1],
                "school": user_info[2],
                "level": user_info[3],
                "gender": user_info[4],
                "role": user_type,
            },
        }

    def __get_teacher_info(self, cursor, username, user_type):
        """获取教师信息"""
        teacher_query = "SELECT jsgh, jsx, zc, xb, yxh FROM T WHERE jsgh = %s"
        cursor.execute(teacher_query, (username,))
        user_info = cursor.fetchone()
        return {
            "user_info": {
                "username": user_info[0],
                "name": user_info[1],
                "school": user_info[4],
                "level": user_info[2],
                "gender": user_info[3],
                "role": user_type,
            },
        }

    def __get_admin_info(self, cursor, username, user_type):
        """获取管理员信息（如果需要）"""
        # 如果管理员有特定信息需要返回，可以在这里添加查询逻辑
        # 目前只返回用户类型
        return {
            "user_info": {
                "username": username,
                "name": "admin",
                "school": "",
                "level": "",
                "gender": "",
                "role": user_type,
            },
        }

    # 其他方法，例如 enroll_student, drop_course 等

    def enroll_student(self, cursor, xh, kch, jsgh):
        try:
            insert_query = """
                INSERT INTO E (xh, kch, jsgh)
                VALUES (%(xh)s, %(kch)s, %(jsgh)s);
            """
            parameters = {
                "xh": xh,
                "kch": kch,
                "jsgh": jsgh,
            }
            cursor.execute(insert_query, parameters)
            return jsonify({"status": "success"})
        except psycopg2.errors.UniqueViolation:
            return jsonify({"status": "failed", "message": "UniqueViolation"})

    def drop_course(self, cursor, xh, kch, jsgh):
        try:
            delete_query = """
                DELETE FROM E
                WHERE xh = %(xh)s AND kch = %(kch)s AND jsgh = %(jsgh)s;
            """
            parameters = {
                "xh": xh,
                "kch": kch,
                "jsgh": jsgh,
            }
            cursor.execute(delete_query, parameters)
            if cursor.rowcount == 0:
                raise Exception("No matching record found for deletion")
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "failed", "message": str(e)})

    def get_enrolled_courses(self, cursor, xh):
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

    def get_partial_schedule(
        self,
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

    def get_teacher_schedule(self, cursor, jsgh):
        query = """
            SELECT
                C.kch,
                C.kcm,
                O.sksj,
                E.xh AS student_id,
                S.xm AS student_name
            FROM
                O
            JOIN
                C ON O.kch = C.kch
            LEFT JOIN
                E ON O.kch = E.kch
            LEFT JOIN
                S ON E.xh = S.xh
            WHERE
                O.jsgh = %(jsgh)s;
        """

        parameters = {"jsgh": jsgh}

        cursor.execute(query, parameters)
        rows = cursor.fetchall()

        teacher_schedule = {}
        for row in rows:
            kch, kcm, sksj, student_id, student_name = row
            if kch not in teacher_schedule:
                teacher_schedule[kch] = {
                    "kch": kch,
                    "kcm": kcm,
                    "sksj": sksj,
                    "student_info": [],
                }
            teacher_schedule[kch]["student_info"].append(
                {"xh": student_id, "xm": student_name}
            )

        return jsonify(
            {
                "total_courses": len(teacher_schedule),
                "course_info": list(teacher_schedule.values()),
            }
        )
