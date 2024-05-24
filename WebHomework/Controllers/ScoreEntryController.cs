using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebHomework.Data;
using WebHomework.Models;

namespace WebHomework.Controllers
{
    public class ScoreEntryController : BaseController
    {
        public ScoreEntryController(WebHomeworkContext context) : base(context)
        {
        }

        public async Task<IActionResult> Index()
        {
            var teacherNo = HttpContext.Session.GetString("UserNo");
            if (string.IsNullOrEmpty(teacherNo))
            {
                return RedirectToAction("Login", "Passwords");
            }

            var viewModel = new ScoreEntryViewModel
            {
                TeacherCourse = await _context.TeacherCourse.Where(tc => tc.TeacherNO == teacherNo).ToListAsync(),
                Course = await _context.Course.ToListAsync(),
                StudentCourse = await _context.StudentCourse.ToListAsync(),
                Student = await _context.Student.ToListAsync()
            };

            return View(viewModel);
        }

        public async Task<IActionResult> GetStudentScores(string courseNo)
        {
            var students = await (from sc in _context.StudentCourse
                                  join s in _context.Student on sc.StudentNO equals s.StudentNO
                                  where sc.CourseNO == courseNo
                                  select new
                                  {
                                      sc.StudentNO,
                                      s.StudentName,
                                      sc.Score
                                  }).ToListAsync();

            return Json(students);
        }

        [HttpPost]
        public async Task<IActionResult> SubmitScores([FromBody] List<StudentCourse> studentCourses)
        {
            if (studentCourses != null && studentCourses.Count > 0)
            {
                foreach (var studentCourse in studentCourses)
                {
                    var existingRecord = await _context.StudentCourse.FirstOrDefaultAsync(sc => sc.StudentNO == studentCourse.StudentNO && sc.CourseNO == studentCourse.CourseNO);
                    if (existingRecord != null)
                    {
                        existingRecord.Score = studentCourse.Score;
                    }
                }

                await _context.SaveChangesAsync();
            }

            return Ok();
        }
    }
}
