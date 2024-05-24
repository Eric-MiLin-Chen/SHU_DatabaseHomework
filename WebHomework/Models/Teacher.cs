using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WebHomework.Models
{
    [Table("Teacher")]
    public class Teacher
    {
        [Key]
        [Column("TeacherNO")]
        public string TeacherNO { get; set; }

        [Column("TeacherName")]
        public string TeacherName { get; set; }

        [Column("TeacherTitle")]
        public string TeacherTitle { get; set; }

        [Column("Gender")]
        public string Gender { get; set; }

        [Column("DepartmentNO")]
        public string DepartmentNO { get; set; }
    }
}
