using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebHomework.Data;
using WebHomework.Models;

namespace WebHomework.Controllers
{
    public class AdministratorsController : BaseController
    {
        public AdministratorsController(WebHomeworkContext context) : base(context)
        {
        }

        public IActionResult Home()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> SetUserNo(string userno)
        {
            if (string.IsNullOrEmpty(userno))
            {
                return BadRequest("UserNo cannot be null or empty");
            }

            HttpContext.Session.SetString("GetUserNo", userno);

            // 查询并设置当前查询用户的身份
            var user = await _context.Password.SingleOrDefaultAsync(p => p.UserNO == userno);
            if (user != null)
            {
                HttpContext.Session.SetString("GetUserIdentity", user.UserIdentity);
            }

            return NoContent(); // 不返回任何内容
        }

        // GET: Courses
        public async Task<IActionResult> Index()
        {
            var UserNo = HttpContext.Session.GetString("GetUserNo");
            var UserIdentity = HttpContext.Session.GetString("GetUserIdentity");


            List<StudentCourse> studentCourses = new List<StudentCourse>();
            List<Course> courses = new List<Course>();
            List<TeacherCourse> teacherCourses = new List<TeacherCourse>();
            List<Teacher> teachers = new List<Teacher>();

            if (UserIdentity == "2") // 学生
            {
                // 查询学生选课信息
                studentCourses = await _context.StudentCourse
                    .Where(sc => sc.StudentNO == UserNo)
                    .ToListAsync();

                // 获取所有课程编号和教师编号
                var courseNos = studentCourses.Select(sc => sc.CourseNO).Distinct().ToList();
                var teacherNums = studentCourses.Select(sc => sc.TeacherNum).Distinct().ToList();

                // 查询相关课程信息
                courses = await _context.Course
                    .Where(c => courseNos.Contains(c.CourseNO))
                    .ToListAsync();

                // 查询相关教师课程信息
                teacherCourses = await _context.TeacherCourse
                    .Where(tc => courseNos.Contains(tc.CourseNO) && teacherNums.Contains(tc.TeacherNum))
                    .ToListAsync();

                // 获取所有教师编号
                var teacherNos = teacherCourses.Select(tc => tc.TeacherNO).Distinct().ToList();

                // 查询相关教师信息
                teachers = await _context.Teacher
                    .Where(t => teacherNos.Contains(t.TeacherNO))
                    .ToListAsync();
            }
            else if (UserIdentity == "1") // 教师
            {
                // 查询教师教授的课程信息
                teacherCourses = await _context.TeacherCourse
                    .Where(tc => tc.TeacherNO == UserNo)
                    .ToListAsync();

                // 获取所有课程编号
                var courseNos = teacherCourses.Select(tc => tc.CourseNO).Distinct().ToList();

                // 查询相关课程信息
                courses = await _context.Course
                    .Where(c => courseNos.Contains(c.CourseNO))
                    .ToListAsync();

                // 查询所有教师课程对应的学生课程记录
                studentCourses = await _context.StudentCourse
                    .Where(sc => courseNos.Contains(sc.CourseNO))
                    .ToListAsync();

                // 获取所有教师编号
                var teacherNos = teacherCourses.Select(tc => tc.TeacherNO).Distinct().ToList();

                // 查询相关教师信息
                teachers = await _context.Teacher
                    .Where(t => teacherNos.Contains(t.TeacherNO))
                    .ToListAsync();
            }

            // 创建视图模型
            var viewModel = new StudentCourseViewModel
            {
                StudentCourse = studentCourses ?? new List<StudentCourse>(),
                Course = courses ?? new List<Course>(),
                TeacherCourse = teacherCourses ?? new List<TeacherCourse>(),
                Teacher = teachers ?? new List<Teacher>()
            };

            ViewBag.UserIdentity = UserIdentity;

            return View(viewModel);
        }

        public async Task<IActionResult> Delete()
        {
            var UserNo = HttpContext.Session.GetString("GetUserNo");
            var UserIdentity = HttpContext.Session.GetString("GetUserIdentity");


            List<StudentCourse> studentCourses = new List<StudentCourse>();
            List<Course> courses = new List<Course>();
            List<TeacherCourse> teacherCourses = new List<TeacherCourse>();
            List<Teacher> teachers = new List<Teacher>();

            if (UserIdentity == "2") // 学生
            {
                // 查询学生选课信息
                studentCourses = await _context.StudentCourse
                    .Where(sc => sc.StudentNO == UserNo)
                    .ToListAsync();

                // 获取所有课程编号和教师编号
                var courseNos = studentCourses.Select(sc => sc.CourseNO).Distinct().ToList();
                var teacherNums = studentCourses.Select(sc => sc.TeacherNum).Distinct().ToList();

                // 查询相关课程信息
                courses = await _context.Course
                    .Where(c => courseNos.Contains(c.CourseNO))
                    .ToListAsync();

                // 查询相关教师课程信息
                teacherCourses = await _context.TeacherCourse
                    .Where(tc => courseNos.Contains(tc.CourseNO) && teacherNums.Contains(tc.TeacherNum))
                    .ToListAsync();

                // 获取所有教师编号
                var teacherNos = teacherCourses.Select(tc => tc.TeacherNO).Distinct().ToList();

                // 查询相关教师信息
                teachers = await _context.Teacher
                    .Where(t => teacherNos.Contains(t.TeacherNO))
                    .ToListAsync();
            }
            else if (UserIdentity == "1") // 教师
            {
                // 查询教师教授的课程信息
                teacherCourses = await _context.TeacherCourse
                    .Where(tc => tc.TeacherNO == UserNo)
                    .ToListAsync();

                // 获取所有课程编号
                var courseNos = teacherCourses.Select(tc => tc.CourseNO).Distinct().ToList();

                // 查询相关课程信息
                courses = await _context.Course
                    .Where(c => courseNos.Contains(c.CourseNO))
                    .ToListAsync();

                // 查询所有教师课程对应的学生课程记录
                studentCourses = await _context.StudentCourse
                    .Where(sc => courseNos.Contains(sc.CourseNO))
                    .ToListAsync();

                // 获取所有教师编号
                var teacherNos = teacherCourses.Select(tc => tc.TeacherNO).Distinct().ToList();

                // 查询相关教师信息
                teachers = await _context.Teacher
                    .Where(t => teacherNos.Contains(t.TeacherNO))
                    .ToListAsync();
            }

            // 创建视图模型
            var viewModel = new StudentCourseViewModel
            {
                StudentCourse = studentCourses ?? new List<StudentCourse>(),
                Course = courses ?? new List<Course>(),
                TeacherCourse = teacherCourses ?? new List<TeacherCourse>(),
                Teacher = teachers ?? new List<Teacher>()
            };

            ViewBag.UserIdentity = UserIdentity;

            return View(viewModel);
        }

        public async Task<IActionResult> StudentDeleteCourse(string courseNo)
        {
            var studentNo = HttpContext.Session.GetString("GetUserNo");


            var studentCourse = await _context.StudentCourse
                .Where(sc => sc.StudentNO == studentNo && sc.CourseNO == courseNo)
                .FirstOrDefaultAsync();

            if (studentCourse == null)
            {
                return Json(new { success = false, message = "未找到选课信息" });
            }

            _context.StudentCourse.Remove(studentCourse);
            await _context.SaveChangesAsync();

            return Json(new { success = true, message = "退课成功" });
        }

        [HttpPost]
        public async Task<IActionResult> TeacherDeleteCourse(string courseNo, string teacherNo)
        {
            var teacherCourse = await _context.TeacherCourse
                .Where(tc => tc.CourseNO == courseNo && tc.TeacherNum == teacherNo)
                .FirstOrDefaultAsync();

            if (teacherCourse == null)
            {
                return Json(new { success = false, message = "未找到课程信息" });
            }

            var studentCourses = await _context.StudentCourse
                .Where(sc => sc.CourseNO == courseNo && sc.TeacherNum == teacherNo)
                .ToListAsync();

            using (var transaction = await _context.Database.BeginTransactionAsync())
            {
                try
                {
                    // 删除指定的学生课程记录
                    if (studentCourses.Any())
                    {
                        _context.StudentCourse.RemoveRange(studentCourses);
                        await _context.SaveChangesAsync();
                    }

                    // 删除指定的教师课程记录
                    _context.TeacherCourse.Remove(teacherCourse);
                    await _context.SaveChangesAsync();

                    // 获取所有受影响的教师课程记录，并更新 TeacherNum
                    var affectedTeacherCourses = await _context.TeacherCourse
                        .Where(tc => tc.CourseNO == courseNo && string.Compare(tc.TeacherNum, teacherNo) > 0)
                        .OrderBy(tc => tc.TeacherNum)
                        .ToListAsync();

                    foreach (var tc in affectedTeacherCourses)
                    {
                        int currentTeacherNum = int.Parse(tc.TeacherNum);
                        tc.TeacherNum = (currentTeacherNum - 1).ToString();
                    }

                    await _context.SaveChangesAsync();

                    // 获取所有受影响的学生课程记录，并更新 TeacherNum
                    var affectedStudentCourses = await _context.StudentCourse
                        .Where(sc => sc.CourseNO == courseNo && string.Compare(sc.TeacherNum, teacherNo) > 0)
                        .OrderBy(sc => sc.TeacherNum)
                        .ToListAsync();

                    foreach (var sc in affectedStudentCourses)
                    {
                        int currentTeacherNum = int.Parse(sc.TeacherNum);
                        sc.TeacherNum = (currentTeacherNum - 1).ToString();
                    }

                    await _context.SaveChangesAsync();

                    await transaction.CommitAsync();

                    return Json(new { success = true, message = "关课成功" });
                }
                catch (Exception ex)
                {
                    await transaction.RollbackAsync();
                    return Json(new { success = false, message = $"关课失败: {ex.Message}" });
                }
            }
        }


        public IActionResult Query()
        {
            if (HttpContext.Session.GetString("GetUserIdentity") == "2")
            {
                return RedirectToAction("StudentQuery");
            }
            else
            {
                return RedirectToAction("TeacherQuery");
            }
        }

        public IActionResult StudentQuery()
        {
            return View();
        }

        public IActionResult TeacherQuery()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> StudentQuery(string courseNo, string courseName, string courseCredit, string teacherNum, string teacherName, string courseTime)
        {
            var query = from tc in _context.TeacherCourse
                        join c in _context.Course on tc.CourseNO equals c.CourseNO
                        join t in _context.Teacher on tc.TeacherNO equals t.TeacherNO
                        select new { tc, c, t };

            if (!string.IsNullOrEmpty(courseNo))
            {
                query = query.Where(q => q.c.CourseNO.Contains(courseNo));
            }
            if (!string.IsNullOrEmpty(courseName))
            {
                query = query.Where(q => q.c.CourseName.Contains(courseName));
            }
            if (!string.IsNullOrEmpty(courseCredit))
            {
                query = query.Where(q => q.c.Credits.Contains(courseCredit));
            }
            if (!string.IsNullOrEmpty(teacherNum))
            {
                query = query.Where(q => q.tc.TeacherNum.Contains(teacherNum));
            }
            if (!string.IsNullOrEmpty(teacherName))
            {
                query = query.Where(q => q.t.TeacherName.Contains(teacherName));
            }
            if (!string.IsNullOrEmpty(courseTime))
            {
                query = query.Where(q => q.tc.CourseTime.Contains(courseTime));
            }

            var result = await query.OrderBy(q => q.c.CourseNO).ThenBy(q => q.tc.TeacherNum).ToListAsync();

            return Json(result);
        }

        [HttpPost]
        public async Task<IActionResult> TeacherQuery(string courseNo, string courseName, string courseCredit)
        {
            var query = from c in _context.Course
                        join tc in _context.TeacherCourse on c.CourseNO equals tc.CourseNO into tcGroup
                        from tc in tcGroup.DefaultIfEmpty()
                        join t in _context.Teacher on tc.TeacherNO equals t.TeacherNO into tGroup
                        from t in tGroup.DefaultIfEmpty()
                        select new { tc, c, t };

            if (!string.IsNullOrEmpty(courseNo))
            {
                query = query.Where(q => q.c.CourseNO.Contains(courseNo));
            }
            if (!string.IsNullOrEmpty(courseName))
            {
                query = query.Where(q => q.c.CourseName.Contains(courseName));
            }
            if (!string.IsNullOrEmpty(courseCredit))
            {
                query = query.Where(q => q.c.Credits.Contains(courseCredit));
            }

            var result = await query.OrderBy(q => q.c.CourseNO).ToListAsync();

            return Json(result);
        }

        [HttpPost]
        public async Task<IActionResult> StudentSelectCourse(string courseNo, string teacherNum)
        {
            var studentNo = HttpContext.Session.GetString("GetUserNo");
            if (string.IsNullOrEmpty(studentNo))
            {
                return Json(new { success = false, message = "请先登录" });
            }

            var studentCourse = new StudentCourse
            {
                StudentNO = studentNo,
                CourseNO = courseNo,
                TeacherNum = teacherNum,
                Score = 0 // 初始分数设为0
            };

            var existingRecord = await _context.StudentCourse
                .Where(sc => sc.StudentNO == studentNo && sc.CourseNO == courseNo)
                .FirstOrDefaultAsync();
            if (existingRecord != null)
            {
                return Json(new { success = false, message = "已选此课程" });
            }

            // 查询当前学生所有课程的上课时间
            var studentCourseTimes = await _context.StudentCourse
                .Join(_context.TeacherCourse,
                      sc => new { sc.CourseNO, sc.TeacherNum },
                      tc => new { tc.CourseNO, tc.TeacherNum },
                      (sc, tc) => new { sc, tc.CourseTime })
                .Where(joined => joined.sc.StudentNO == studentNo)
                .Select(joined => joined.CourseTime)
                .ToListAsync();

            // 查询特定课程的上课时间
            var courseTime = await _context.TeacherCourse
                .Where(tc => tc.CourseNO == courseNo && tc.TeacherNum == teacherNum)
                .Select(tc => tc.CourseTime)
                .FirstOrDefaultAsync();

            // 检查是否有时间冲突
            bool hasConflict = studentCourseTimes.Any(time => time == courseTime);
            if (hasConflict)
            {
                return Json(new { success = false, message = "选课时间冲突" });
            }

            _context.StudentCourse.Add(studentCourse);
            await _context.SaveChangesAsync();

            return Json(new { success = true, message = "选课成功" });
        }

        [HttpPost]
        public async Task<IActionResult> TeacherSelectCourse(string courseNo, string courseTime)
        {
            var teacherNo = HttpContext.Session.GetString("GetUserNo");


            // 检查是否存在重复的CourseNO
            var existingCourse = await _context.TeacherCourse
                .Where(tc => tc.TeacherNO == teacherNo && tc.CourseNO == courseNo)
                .FirstOrDefaultAsync();

            if (existingCourse != null)
            {
                return Json(new { success = false, message = "已开过该课程" });
            }

            // 检查是否存在重复的CourseTime
            var existingTime = await _context.TeacherCourse
                .Where(tc => tc.TeacherNO == teacherNo && tc.CourseTime == courseTime)
                .FirstOrDefaultAsync();

            if (existingTime != null)
            {
                return Json(new { success = false, message = "该上课时间已开课" });
            }

            // 查找当前教师的最大TeacherNum
            var maxTeacherNum = await _context.TeacherCourse
                .Where(tc => tc.CourseNO == courseNo)
                .OrderByDescending(tc => tc.TeacherNum)
                .Select(tc => tc.TeacherNum)
                .FirstOrDefaultAsync();

            string newTeacherNum = "1001";
            if (maxTeacherNum != null)
            {
                if (int.TryParse(maxTeacherNum, out int maxNum))
                {
                    newTeacherNum = (maxNum + 1).ToString();
                }
            }

            // 添加新的TeacherCourse记录
            var newTeacherCourse = new TeacherCourse
            {
                TeacherNO = teacherNo,
                CourseNO = courseNo,
                CourseTime = courseTime,
                TeacherNum = newTeacherNum
            };

            _context.TeacherCourse.Add(newTeacherCourse);
            await _context.SaveChangesAsync();

            return Json(new { success = true, message = "开课成功。" });
        }


    }
}
