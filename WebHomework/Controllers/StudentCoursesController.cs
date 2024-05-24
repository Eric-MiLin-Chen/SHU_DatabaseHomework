using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebHomework.Data;
using WebHomework.Models;

namespace WebHomework.Controllers
{
    public class StudentCoursesController : BaseController
    {
        public StudentCoursesController(WebHomeworkContext context) : base(context)
        {
        }

        // GET: StudentCourses
        public async Task<IActionResult> Index()
        {
            var studentNo = HttpContext.Session.GetString("UserNo");
            if (string.IsNullOrEmpty(studentNo))
            {
                return RedirectToAction("Login", "Passwords");
            }

            // 查询学生选课信息
            var studentCourses = await _context.StudentCourse
                .Where(sc => sc.StudentNO == studentNo)
                .ToListAsync();

            // 获取所有课程编号和教师编号
            var courseNos = studentCourses.Select(sc => sc.CourseNO).Distinct().ToList();
            var teacherNums = studentCourses.Select(sc => sc.TeacherNum).Distinct().ToList();

            // 查询相关课程信息
            var courses = await _context.Course
                .Where(c => courseNos.Contains(c.CourseNO))
                .ToListAsync();

            // 查询相关教师课程信息
            var teacherCourses = await _context.TeacherCourse
                .Where(tc => courseNos.Contains(tc.CourseNO) && teacherNums.Contains(tc.TeacherNum))
                .ToListAsync();

            // 获取所有教师编号
            var teacherNos = teacherCourses.Select(tc => tc.TeacherNO).Distinct().ToList();

            // 查询相关教师信息
            var teachers = await _context.Teacher
                .Where(t => teacherNos.Contains(t.TeacherNO))
                .ToListAsync();

            // 创建视图模型
            var viewModel = new StudentCourseViewModel
            {
                StudentCourse = studentCourses,
                Course = courses,
                TeacherCourse = teacherCourses,
                Teacher = teachers
            };

            return View(viewModel);
        }

        // GET: StudentCourses/Query
        public IActionResult Query()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> Query(string courseNo, string courseName, string courseCredit, string teacherNum, string teacherName, string courseTime)
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
        public async Task<IActionResult> SelectCourse(string courseNo, string teacherNum)
        {
            var studentNo = HttpContext.Session.GetString("UserNo");
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
        public async Task<IActionResult> Delete()
        {
            var studentNo = HttpContext.Session.GetString("UserNo");
            if (string.IsNullOrEmpty(studentNo))
            {
                return RedirectToAction("Login", "Passwords");
            }

            // 查询学生选课信息
            var studentCourses = await _context.StudentCourse
                .Where(sc => sc.StudentNO == studentNo)
                .ToListAsync();

            // 获取所有课程编号和教师编号
            var courseNos = studentCourses.Select(sc => sc.CourseNO).Distinct().ToList();
            var teacherNums = studentCourses.Select(sc => sc.TeacherNum).Distinct().ToList();

            // 查询相关课程信息
            var courses = await _context.Course
                .Where(c => courseNos.Contains(c.CourseNO))
                .ToListAsync();

            // 查询相关教师课程信息
            var teacherCourses = await _context.TeacherCourse
                .Where(tc => courseNos.Contains(tc.CourseNO) && teacherNums.Contains(tc.TeacherNum))
                .ToListAsync();

            // 获取所有教师编号
            var teacherNos = teacherCourses.Select(tc => tc.TeacherNO).Distinct().ToList();

            // 查询相关教师信息
            var teachers = await _context.Teacher
                .Where(t => teacherNos.Contains(t.TeacherNO))
                .ToListAsync();

            // 创建视图模型
            var viewModel = new StudentCourseViewModel
            {
                StudentCourse = studentCourses,
                Course = courses,
                TeacherCourse = teacherCourses,
                Teacher = teachers
            };

            return View(viewModel);
        }
        public async Task<IActionResult> DeleteCourse(string courseNo)
        {
            var studentNo = HttpContext.Session.GetString("UserNo");
            if (string.IsNullOrEmpty(studentNo))
            {
                return Json(new { success = false, message = "请先登录" });
            }

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

    }
}
