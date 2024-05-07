from flask import jsonify
import psycopg2
import random
from pprint import pprint


class UserManager:
    def __init__(self, db_manager, auth_manager):
        self.db_manager = db_manager
        self.auth_manager = auth_manager

    def verify_credentials(self, cursor, username, password, admin_user=False):
        """验证用户凭据并返回用户类型"""
        query = "SELECT mm, qx FROM P WHERE xh = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result and result[0].strip() == password or admin_user == True:
            return result[1]  # 返回用户类型
        return None

    def get_user_info(self, cursor, user_type, username):
        """根据用户类型获取用户信息"""
        user_type = user_type.strip()
        if user_type == "0":
            return self.__get_admin_info(cursor, username, user_type)

        elif user_type == "1":
            return self.__get_teacher_info(cursor, username, user_type)

        elif user_type == "2":
            return self.__get_student_info(cursor, username, user_type)

        return {}

    def __get_student_info(self, cursor, username, user_type):
        """获取学生信息"""
        student_query = "SELECT S.xh, S.xm, I.xymc, S.zdnj, S.xb FROM S, I WHERE S.xh = %s AND S.xyh = I.xyh"
        cursor.execute(student_query, (username,))
        user_info = cursor.fetchone()
        return {
            "status": "success",
            "user_info": {
                "id": user_info[0],
                "name": user_info[1],
                "school": user_info[2],
                "level": user_info[3],
                "gender": user_info[4],
                "role": user_type,
            },
        }

    def __get_teacher_info(self, cursor, username, user_type):
        """获取教师信息"""
        teacher_query = "SELECT T.jsgh, T.jsxm, I.xymc, T.jszc, T.xb FROM T, I WHERE jsgh = %s AND T.xyh = I.xyh"
        cursor.execute(teacher_query, (username,))
        user_info = cursor.fetchone()
        return {
            "status": "success",
            "user_info": {
                "id": user_info[0],
                "name": user_info[1],
                "school": user_info[2],
                "level": user_info[3],
                "gender": user_info[4],
                "role": user_type,
            },
        }

    def __get_admin_info(self, cursor, username, user_type):
        return self.__get_teacher_info(cursor, username, user_type)

    # 学生方法

    def enroll_student_course(self, cursor, xh, kch, jsh):
        try:
            # 查询该学生已经选修的课程的上课时间和课程号
            select_query = """
                SELECT O.sksj, E.kch
                FROM E
                JOIN O ON E.kch = O.kch AND E.jsh = O.jsh
                WHERE E.xh = %(xh)s
            """
            cursor.execute(select_query, {"xh": xh})
            existing_courses = cursor.fetchall()

            # 查询新课程的上课时间和课程号
            select_query = """
                SELECT sksj
                FROM O
                WHERE kch = %(kch)s AND jsh = %(jsh)s
            """
            cursor.execute(select_query, {"kch": kch, "jsh": jsh})
            new_sksj = cursor.fetchone()[0]

            # 检查新课程的上课时间是否与已选修课程的上课时间重复
            for sksj, existing_kch in existing_courses:
                if sksj == new_sksj:
                    # 如果时间重叠，拒绝录入课程并返回失败信息
                    return jsonify(
                        {
                            "status": "failed",
                            "message": "Course schedule conflicts with existing courses.",
                        }
                    )
                if existing_kch == kch:
                    # 如果课程号重复，拒绝录入课程并返回失败信息
                    return jsonify(
                        {
                            "status": "failed",
                            "message": "Course already enrolled by the student.",
                        }
                    )

            # 插入新课程
            insert_query = """
                INSERT INTO E (xh, kch, jsh)
                VALUES (%(xh)s, %(kch)s, %(jsh)s);
            """
            parameters = {
                "xh": xh,
                "kch": kch,
                "jsh": jsh,
            }
            cursor.execute(insert_query, parameters)
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "failed", "message": str(e)})

    def drop_student_course(self, cursor, xh, kch, jsh):
        try:
            delete_query = """
                DELETE FROM E
                WHERE xh = %(xh)s AND kch = %(kch)s AND jsh = %(jsh)s;
            """
            parameters = {
                "xh": xh,
                "kch": kch,
                "jsh": jsh,
            }
            cursor.execute(delete_query, parameters)
            if cursor.rowcount == 0:
                raise Exception("No matching record found for deletion")
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "failed", "message": str(e)})

    def get_student_schedule(self, cursor, xh):
        query = """
            SELECT
                E.kch,
                C.kcm,
                T.jsxm,
                O.sksj,
                C.xf,
                O.jsh,
                C.zdrs
            FROM
                E
            JOIN
                C ON E.kch = C.kch
            JOIN
                O ON E.kch = O.kch AND O.jsh = E.jsh
            JOIN
                T ON O.jsgh = T.jsgh
            WHERE
                E.xh = %(xh)s
            ORDER BY E.kch, O.jsh;
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
                "jsh": row[5],
                "zdrs": row[6],
            }
            for row in rows
        ]

        return jsonify(
            {
                "status": "success",
                "total_count": len(enrolled_courses),
                "course_info": enrolled_courses,
            }
        )

    def get_student_available_course(
        self,
        cursor,
        kch="",
        kcm="",
        xf="",
        jsh="",
        jsxm="",
        sksj="",
    ):
        try:
            # 添加约束条件
            where_conditions = []
            parameters = {}

            if kch:
                where_conditions.append("O.kch = %(kch)s")
                parameters["kch"] = kch
            if kcm:
                where_conditions.append("C.kcm = %(kcm)s")
                parameters["kcm"] = kcm
            if xf:
                where_conditions.append("C.xf = %(xf)s")
                parameters["xf"] = xf
            if jsh:
                where_conditions.append("O.jsh = %(jsh)s")
                parameters["jsh"] = jsh
            if jsxm:
                where_conditions.append("T.jsxm = %(jsxm)s")
                parameters["jsxm"] = jsxm
            if sksj:
                where_conditions.append("O.sksj = %(sksj)s")
                parameters["sksj"] = sksj

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
            schedule_query += f" ORDER BY O.kch, O.jsh;"

            # 执行分页查询
            cursor.execute(schedule_query, parameters)
            rows = cursor.fetchall()
            available_course = [
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
            ans = jsonify(
                {
                    "total_count": len(available_course),
                    "course_info": available_course,
                    "status": "success",
                }
            )
            pprint(ans)
            # 将总数和分页结果一起返回
            return ans
        except Exception as e:
            # 捕获可能的异常，并返回失败信息
            error_msg = "Failed to retrieve available courses. Error: {}".format(str(e))
            return jsonify({"error": error_msg, "status": "failed"})

    # 教师方法

    def get_teacher_schedule(self, cursor, jsgh):
        query = """
            SELECT
                C.kch,
                C.kcm,
                O.sksj,
                C.xf,
                C.zdrs
            FROM
                O
            JOIN
                C ON O.kch = C.kch
            WHERE
                O.jsgh = %(jsgh)s
            ORDER BY C.kch;
        """

        parameters = {"jsgh": jsgh}

        cursor.execute(query, parameters)
        rows = cursor.fetchall()

        teacher_schedule = {}
        for row in rows:
            kch, kcm, sksj, xf, zdrs = row
            if kch not in teacher_schedule:
                teacher_schedule[kch] = {
                    "kch": kch,
                    "kcm": kcm,
                    "sksj": sksj,
                    "xf": xf,
                    "zdrs": zdrs,
                }

        ans = jsonify(
            {
                "status": "success",
                "total_courses": len(teacher_schedule),
                "course_info": list(teacher_schedule.values()),
            }
        )
        pprint(ans)
        return ans

    def get_student_info(self, cursor, jsgh, kch):
        query = """
            SELECT
                E.xh,
                S.xm,
                E.cj
            FROM
                E
            JOIN
                S ON E.xh = S.xh
            JOIN
                O ON O.jsgh = %(jsgh)s
            WHERE
                E.kch = %(kch)s AND E.jsh = O.jsh
        """

        parameters = {"jsgh": jsgh, "kch": kch}

        cursor.execute(query, parameters)
        rows = cursor.fetchall()

        student_info = []
        for row in rows:
            xh, xm, cj = row
            student_info.append(
                {
                    "xh": xh,
                    "xm": xm,
                    "cj": cj,
                }
            )

        ans = jsonify(
            {
                "status": "success",
                "total": len(student_info),
                "student_info": student_info,
            }
        )
        pprint(ans)
        return ans

    def manage_student_score(self, cursor, jsgh, kch, xh, cj):
        try:
            # 检查成绩格式是否合法
            if not (cj.isdigit() and 0 <= int(cj) <= 100):
                return {
                    "status": "failed",
                    "message": "Invalid score. Score must be an integer between 0 and 100.",
                }

            get_jsh_query = "SELECT jsh FROM O WHERE jsgh = %(jsgh)s AND kch = %(kch)s"
            parameters = {"jsgh": jsgh, "kch": kch}

            cursor.execute(get_jsh_query, parameters)
            rows = cursor.fetchall()

            jsh = None
            if len(rows) == 0:
                return {"status": "failed", "message": "No matching record found"}
            else:
                jsh = rows[0]

            insert_query = """
                UPDATE E SET cj = %(cj)s WHERE xh = %(xh)s AND kch = %(kch)s;
            """
            parameters = {"xh": xh, "kch": kch, "jsh": jsh, "cj": cj}
            cursor.execute(insert_query, parameters)
            return {"status": "success"}
        except psycopg2.errors.UniqueViolation:
            return {"status": "failed", "message": "UniqueViolation"}

    # 管理员方法

    def get_teacher_available_course(self, cursor, kch="", kcm="", xf=""):
        # 添加约束条件
        schedule_query = """
            SELECT DISTINCT
                C.kch,
                C.kcm,
                C.xf,
                C.zdrs
            FROM
                C
            JOIN
                O ON C.kch = O.kch
            JOIN
                T ON O.jsgh = T.jsgh
        """
        where_conditions = []
        parameters = {}

        if kch != "":
            where_conditions.append("C.kch = %(kch)s")
            parameters["kch"] = kch
        if kcm != "":
            where_conditions.append("C.kcm = %(kcm)s")
            parameters["kcm"] = kcm
        if xf != "":
            where_conditions.append("C.xf = %(xf)s")
            parameters["xf"] = xf

        if where_conditions:
            schedule_query += " WHERE " + " AND ".join(where_conditions)

        schedule_query += f" ORDER BY C.kch"

        cursor.execute(schedule_query, parameters)
        rows = cursor.fetchall()
        teacher_available_course = [
            {
                "kch": row[0],
                "kcm": row[1],
                "xf": row[2],
                "zdrs": row[3],
            }
            for row in rows
        ]

        # 将总数和分页结果一起返回
        ans = {
            "total_count": len(teacher_available_course),
            "course_info": teacher_available_course,
            "status": "success",
        }

        pprint(ans)

        return ans

    def enroll_teacher_course(self, cursor, jsgh, kch, sksj):
        try:
            # 检查老师在O表中所开的课程上课时间是否有重复
            check_existing_schedule_query = (
                "SELECT 1 FROM O WHERE jsgh = %(jsgh)s AND sksj = %(sksj)s"
            )
            cursor.execute(check_existing_schedule_query, {"jsgh": jsgh, "sksj": sksj})
            existing_schedule = cursor.fetchone()
            if existing_schedule:
                return {
                    "status": "failed",
                    "message": "Duplicate class schedule for the teacher.",
                }

            # 查询同课程号的教师号，并生成新增课程的教师号
            get_max_jsh_query = (
                "SELECT MAX(CAST(jsh AS INTEGER)) FROM O WHERE kch = %(kch)s"
            )
            cursor.execute(get_max_jsh_query, {"kch": kch})
            max_jsh = cursor.fetchone()[0]
            if max_jsh is None:
                new_jsh = "1"
            else:
                new_jsh = str(int(max_jsh) + 1)

            # 插入新课程
            insert_course_query = """
                INSERT INTO O (jsgh, kch, jsh, sksj)
                VALUES (%(jsgh)s, %(kch)s, %(jsh)s, %(sksj)s);
            """
            parameters = {
                "jsgh": jsgh,
                "kch": kch,
                "jsh": new_jsh,
                "sksj": sksj,
            }
            cursor.execute(insert_course_query, parameters)

            return {"status": "success"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def drop_teacher_course(self, cursor, jsgh, kch, sksj):
        try:
            # 查询被删除课程的教师号
            get_deleted_jsh_query = """
                SELECT jsh
                FROM O
                WHERE jsgh = %(jsgh)s AND kch = %(kch)s AND sksj = %(sksj)s;
            """
            parameters = {
                "jsgh": jsgh,
                "kch": kch,
                "sksj": sksj,
            }
            cursor.execute(get_deleted_jsh_query, parameters)
            deleted_jsh = cursor.fetchone()

            # 如果没有找到被删除课程的教师号，则返回失败状态与错误消息
            if not deleted_jsh:
                return jsonify(
                    {
                        "status": "failed",
                        "message": "No matching record found for deletion",
                    }
                )

            deleted_jsh = deleted_jsh[0]  # 提取被删除课程的教师号

            # 删除指定课程
            delete_query = """
                DELETE FROM O
                WHERE jsgh = %(jsgh)s AND kch = %(kch)s AND sksj = %(sksj)s;
            """
            cursor.execute(delete_query, parameters)

            # 更新大于被删除课程的教师号
            update_query = """
                UPDATE O
                SET jsh = jsh - 1
                WHERE kch = %(kch)s AND jsh > %(deleted_jsh)s;
            """
            parameters = {
                "kch": kch,
                "deleted_jsh": deleted_jsh,
            }
            cursor.execute(update_query, parameters)

            # 如果没有匹配的记录被删除，则返回失败状态与错误消息
            if cursor.rowcount == 0:
                return jsonify(
                    {
                        "status": "failed",
                        "message": "No matching record found for deletion",
                    }
                )

            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "failed", "message": str(e)})
