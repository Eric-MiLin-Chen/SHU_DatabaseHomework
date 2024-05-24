using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebHomework.Data;

namespace WebHomework.Controllers
{
    public class StudentsController : BaseController
    {
        public StudentsController(WebHomeworkContext context) : base(context)
        {
        }

        // GET: Students
        public async Task<IActionResult> Index()
        {
            return View(await _context.Student.ToListAsync());
        }
    }
}
