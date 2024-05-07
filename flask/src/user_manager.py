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
        except psycopg2.errors.UniqueViolation:
            return jsonify({"status": "failed", "message": "UniqueViolation"})

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

    def get_partial_open_course(
        self,
        cursor,
        start_position,
        length=20,
        kch="",
        kcm="",
        xf="",
        jsh="",
        jsxm="",
        sksj="",
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

        if kch != "":
            where_conditions.append("O.kch = %(kch)s")
            parameters["kch"] = kch
        if kcm != "":
            where_conditions.append("C.kcm = %(kcm)s")
            parameters["kcm"] = kcm
        if xf != "":
            where_conditions.append("C.xf = %(xf)s")
            parameters["xf"] = xf
        if jsh != "":
            where_conditions.append("O.jsh = %(jsh)s")
            parameters["jsh"] = jsh
        if jsxm != "":
            where_conditions.append("T.jsxm = %(jsxm)s")
            parameters["jsxm"] = jsxm
        if sksj != "":
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
        pprint(
            {
                "total_count": total_count,
                "course_info": partial_schedule,
                "status": "success",
            }
        )
        # 将总数和分页结果一起返回
        return jsonify(
            {
                "total_count": total_count,
                "course_info": partial_schedule,
                "status": "success",
            }
        )

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
                O.jsgh = %(jsgh)s;
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
                    # "student_info": [],
                }

        return jsonify(
            {
                "status": "success",
                "total_courses": len(teacher_schedule),
                "course_info": list(teacher_schedule.values()),
            }
        )

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
        pprint(student_info)
        return jsonify(
            {
                "status": "success",
                "total": len(student_info),
                "student_info": student_info,
            }
        )

    def manage_student_score(self, cursor, jsgh, kch, xh, cj):
        try:
            get_jsh_query = "SELECT jsh FROM O WHERE jsgh = %s AND kch = %s"
            parameters = (jsgh, kch)

            cursor.execute(get_jsh_query, parameters)
            rows = cursor.fetchall()

            jsh = None
            if len(rows) == 0:
                return jsonify(
                    {"status": "failed", "message": "No matching record found"}
                )
            else:
                jsh = rows[0]

            insert_query = """
                UPDATE E SET cj = %(cj)s WHERE xh = %(xh)s AND kch = %(kch)s;
            """
            parameters = {"xh": xh, "kch": kch, "jsh": jsh, "cj": cj}
            cursor.execute(insert_query, parameters)
            return jsonify({"status": "success"})
        except psycopg2.errors.UniqueViolation:
            return jsonify({"status": "failed", "message": "UniqueViolation"})

    # 管理员方法

    def get_course(self, cursor, kch, kcm, xf, role=1):
        # 添加约束条件
        schedule_query = """
                SELECT DISTINCT
                    C.kch,
                    C.kcm,
                    O.jsh,
                    T.jsxm,
                    O.sksj,
                    C.xf,
                    C.zdrs
                FROM
                    C
                JOIN
                    O ON C.kch = O.kch
                JOIN
                    T ON O.jsgh = T.jsgh
                ORDER BY
                    C.kch
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

        # 构建 SQL 查询的语句
        # if role == 0:
        #     schedule_query = """
        #         SELECT
        #             C.kch,
        #             C.kcm,
        #             O.jsh,
        #             T.jsxm,
        #             O.sksj,
        #             C.xf,
        #             C.zdrs
        #         FROM
        #             C
        #         JOIN
        #             O ON C.kch = O.kch
        #         JOIN
        #             T ON O.jsgh = T.jsgh
        #         ORDER BY
        #             C.kch
        # """
        # elif role == 1:
        #     schedule_query = """
        #         SELECT DISTINCT
        #             C.kch,
        #             C.kcm,
        #             O.jsh,
        #             T.jsxm,
        #             O.sksj,
        #             C.xf,
        #             C.zdrs
        #         FROM
        #             C
        #         JOIN
        #             O ON C.kch = O.kch
        #         JOIN
        #             T ON O.jsgh = T.jsgh
        #         ORDER BY
        #             C.kch
        # """
        # else:
        #     return

        if where_conditions:
            schedule_query += " WHERE " + " AND ".join(where_conditions)

        cursor.execute(schedule_query, parameters)
        rows = cursor.fetchall()
        partial_schedule = [
            {
                "kch": row[0],
                "kcm": row[1],
                "xf": row[5],
                "zdrs": row[6],
            }
            for row in rows
        ]

        # 将总数和分页结果一起返回
        result = {
            "total_count": len(partial_schedule),
            "course_info": partial_schedule,
            "status": "success",
        }

        return result

    def enroll_teacher_course(self, cursor, jsgh, kch, sksj=None):
        try:
            # 判断同教师在相同sksj中是否已有课程
            day = ["一", "二", "三", "四", "五"]

            if sksj == None:
                time = random.randint(1, 6) * 2 - 1
                sksj = f"{day[random.randint(0, 4)]}{time}-{time+1}"
                pprint(sksj)

            check_course_query = "SELECT COUNT(*) FROM O WHERE jsgh = %s AND sksj = %s"
            cursor.execute(check_course_query, (jsgh, sksj))
            existing_courses_count = cursor.fetchone()[0]

            if existing_courses_count > 0:
                return {"status": "error", "message": "Course time conflict"}

            # 查询同课程号下所有开课的jsgh并保存入列表
            all_jsgh_query = "SELECT jsgh FROM O WHERE kch = %s"
            cursor.execute(all_jsgh_query, (kch,))
            all_jsgh_list = [row[0] for row in cursor.fetchall()]

            # 分配教师号，从最小值开始递增，直到找到第一个不冲突的教师号
            new_jsgh = 1001
            while new_jsgh in all_jsgh_list:
                new_jsgh += 1

            # 插入记录到表O
            insert_query = "INSERT INTO O (jsgh, kch, jsh, sksj) VALUES (%(jsgh)s, %(kch)s, %(jsh)s, %(sksj)s)"
            parameters = {
                "jsgh": jsgh,
                "kch": kch,
                "jsh": new_jsgh,
                "sksj": sksj,
            }
            cursor.execute(insert_query, parameters)

            return {"status": "success"}

        except psycopg2.errors.UniqueViolation:
            return jsonify({"status": "failed", "message": "UniqueViolation"})

    def drop_teacher_course(self, cursor, jsgh, kch, sksj):
        try:
            delete_query = """
                DELETE FROM O
                WHERE jsgh = %(jsgh)s AND kch = %(kch)s AND sksj = %(sksj)s;
            """
            parameters = {
                "jsgh": jsgh,
                "kch": kch,
                "sksj": sksj,
            }
            cursor.execute(delete_query, parameters)
            if cursor.rowcount == 0:
                raise Exception("No matching record found for deletion")
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "failed", "message": str(e)})
