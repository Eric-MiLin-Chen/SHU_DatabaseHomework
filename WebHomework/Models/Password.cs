using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WebHomework.Models
{
    [Table("Password")]
    public class Password
    {
        [Key]
        [Required(ErrorMessage = "请输入用户账号")]
        [Column("UserNO")]//用户账号
        public string UserNO { get; set; }

        [Required(ErrorMessage = "请输入密码")]
        [Column("Password")]//密码
        public string Passwords { get; set; }

        [Column("UserIdentity")]//用户身份
        public string UserIdentity { get; set; }
    }
}
