using System.ComponentModel.DataAnnotations.Schema;

namespace WebHomework.Models
{
    [Table("TeacherCourse")]
    public class TeacherCourse
    {
        [Column("TeacherNO")]
        public string TeacherNO { get; set; }

        [Column("CourseNO")]
        public string CourseNO { get; set; }

        [Column("TeacherNum")]
        public string TeacherNum { get; set; }

        [Column("CourseTime")]
        public string CourseTime { get; set; }
    }
}
