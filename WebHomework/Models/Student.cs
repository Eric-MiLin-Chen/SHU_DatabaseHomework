using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WebHomework.Models
{
    [Table("Student")]
    public class Student
    {
        [Key]
        [Column("StudentNO")]
        public string StudentNO { get; set; }

        [Column("StudentName")]
        public string StudentName { get; set; }

        [Column("Gender")]
        public string Gender { get; set; }

        [Column("Grade")]
        public string Grade { get; set; }

        [Column("GPA")]
        public string GPA { get; set; }

        [Column("DepartmentNO")]
        public string DepartmentNO { get; set; }
    }
}
