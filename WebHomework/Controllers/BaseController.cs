using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.EntityFrameworkCore;
using WebHomework.Data;

public class BaseController : Controller
{
    protected readonly WebHomeworkContext _context;

    public BaseController(WebHomeworkContext context)
    {
        _context = context;
    }

    public override async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
    {
        var userNo = HttpContext.Session.GetString("UserNo");
        var identity = HttpContext.Session.GetString("UserIdentity");
        var setUser = HttpContext.Session.GetString("GetUserNo"); // 获取当前查询用户的编号
        var userIdentity = HttpContext.Session.GetString("GetUserIdentity"); // 获取当前查询用户的身份

        if (identity == "1") // 若为教师身份
        {
            if (!string.IsNullOrEmpty(userNo))
            {
                var teacher = await _context.Teacher.SingleOrDefaultAsync(t => t.TeacherNO == userNo);
                if (teacher != null)
                {
                    var department = await _context.Department.FindAsync(teacher.DepartmentNO);
                    ViewBag.TeacherNo = teacher.TeacherNO;
                    ViewBag.TeacherName = teacher.TeacherName;
                    ViewBag.TeacherTitle = teacher.TeacherTitle;
                    ViewBag.Gender = teacher.Gender;
                    ViewBag.DepartmentName = department?.DepartmentName;
                }
            }
        }
        else if (identity == "2") // 若为学生身份
        {
            if (!string.IsNullOrEmpty(userNo))
            {
                var student = await _context.Student.SingleOrDefaultAsync(s => s.StudentNO == userNo);
                if (student != null)
                {
                    var department = await _context.Department.FindAsync(student.DepartmentNO);
                    ViewBag.StudentNo = student.StudentNO;
                    ViewBag.StudentName = student.StudentName;
                    ViewBag.StudentGrade = student.Grade;
                    ViewBag.Gender = student.Gender;
                    ViewBag.DepartmentName = department?.DepartmentName;
                }
            }
        }
        else if (identity == "0") // 若为管理员身份
        {
            if (!string.IsNullOrEmpty(setUser))
            {
                var user = await _context.Password.SingleOrDefaultAsync(p => p.UserNO == setUser);
                if (user != null)
                {
                    HttpContext.Session.SetString("GetUserIdentity", user.UserIdentity); // 更新当前查询用户的身份
                    if (user.UserIdentity == "1") // 若为老师
                    {
                        var teacher = await _context.Teacher.SingleOrDefaultAsync(t => t.TeacherNO == setUser);
                        if (teacher != null)
                        {
                            var department = await _context.Department.FindAsync(teacher.DepartmentNO);
                            ViewBag.UserNo = setUser;
                            ViewBag.UserName = teacher.TeacherName;
                            ViewBag.UserGrade = teacher.TeacherTitle;
                            ViewBag.Gender = teacher.Gender;
                            ViewBag.DepartmentName = department?.DepartmentName;
                        }
                    }
                    else if (user.UserIdentity == "2") // 若为学生
                    {
                        var student = await _context.Student.SingleOrDefaultAsync(s => s.StudentNO == setUser);
                        if (student != null)
                        {
                            var department = await _context.Department.FindAsync(student.DepartmentNO);
                            ViewBag.UserNo = setUser;
                            ViewBag.UserName = student.StudentName;
                            ViewBag.UserGrade = student.Grade;
                            ViewBag.Gender = student.Gender;
                            ViewBag.DepartmentName = department?.DepartmentName;
                        }
                    }
                }
            }
        }

        await next();
    }
}