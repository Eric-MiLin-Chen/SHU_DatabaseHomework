using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Mvc;
using WebHomework.Data;
using WebHomework.Models;

namespace WebHomework.Controllers
{
    public class PasswordsController : Controller
    {
        private readonly WebHomeworkContext _context;

        public PasswordsController(WebHomeworkContext context)
        {
            _context = context;
        }

        public IActionResult Login()
        {
            return View();
        }

       public static string ComputeSha256Hash(string rawData)//调用哈希函数
        {
            using (SHA256 sha256Hash = SHA256.Create())
            {
                byte[] bytes = sha256Hash.ComputeHash(Encoding.UTF8.GetBytes(rawData));
                StringBuilder builder = new StringBuilder();
                for (int i = 0; i < bytes.Length; i++)
                {
                    builder.Append(bytes[i].ToString("x2"));
                }
                return builder.ToString();
            }
        }


        [HttpPost]
        public IActionResult Login(Password model)
        {
            string hashedPassword = ComputeSha256Hash(model.Passwords);//将密码哈希

            var user = _context.Password.SingleOrDefault(m => m.UserNO == model.UserNO && m.Passwords == hashedPassword);//验证密码
            if (user != null)
            {
                HttpContext.Session.SetString("UserNo", user.UserNO);//将用户信息存入Session
                HttpContext.Session.SetString("UserIdentity", user.UserIdentity);
                if (user.UserIdentity == "1")
                    return RedirectToAction("Index", "Teachers");
                else if (user.UserIdentity == "2")
                    return RedirectToAction("Index", "Students");
                else if (user.UserIdentity == "0")
                    return RedirectToAction("Home", "Administrators");
            }
            string message = "用户名或密码错误";
            ViewBag.ErrorMessage = message;
            return View();
        }



        [HttpPost]
        public IActionResult Logout()
        {
            HttpContext.Session.Remove("UserNo");
            HttpContext.Session.Remove("UserIdentity");
            HttpContext.Session.Remove("GetUserNo");
            HttpContext.Session.Remove("GetUserIdentity");
            return RedirectToAction("Login", "Passwords");
        }

    }
}
