using System.ComponentModel.DataAnnotations.Schema;

namespace WebHomework.Models
{
    [Table("StudentCourse")]
    public class StudentCourse
    {
        [Column("StudentNO")]
        public string StudentNO { get; set; }

        [Column("CourseNO")]
        public string CourseNO { get; set; }

        [Column("TeacherNum")]
        public string TeacherNum { get; set; }

        [Column("Score")]
        public int Score { get; set; }
    }
}
