using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebHomework.Data;
using WebHomework.Models;

namespace WebHomework.Controllers
{
    public class TeacherCoursesController : BaseController
    {
        public TeacherCoursesController(WebHomeworkContext context) : base(context)
        {
        }

        public async Task<IActionResult> Index()
        {
            var teacherNo = HttpContext.Session.GetString("UserNo");
            if (string.IsNullOrEmpty(teacherNo))
            {
                return RedirectToAction("Login", "Passwords");
            }

            var teacherCourses = await _context.TeacherCourse
                .Where(tc => tc.TeacherNO == teacherNo)
                .ToListAsync();

            var courses = await _context.Course
                .Where(c => teacherCourses.Select(tc => tc.CourseNO).Contains(c.CourseNO))
                .ToListAsync();

            var viewModel = new TeacherCourseViewModel
            {
                TeacherCourse = teacherCourses,
                Course = courses
            };

            return View(viewModel);
        }
    }
}
