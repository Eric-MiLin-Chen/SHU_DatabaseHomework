using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebHomework.Data;

namespace WebHomework.Controllers
{
    public class TeachersController : BaseController
    {
        public TeachersController(WebHomeworkContext context) : base(context)
        {
        }

        // GET: Teachers
        public async Task<IActionResult> Index()
        {
            return View(await _context.Teacher.ToListAsync());
        }

        
    }
}
