using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WebHomework.Models
{
    [Table("Course")]
    public class Course
    {
        [Key]
        [Column("CourseNO")]
        public string CourseNO { get; set; }

        [Column("CourseName")]
        public string CourseName { get; set; }

        [Column("Credits")]
        public string Credits { get; set; }

        [Column("MaxStudentNum")]
        public string MaxStudentNum { get; set; }

        [Column("DepartmentNO")]
        public string DepartmentNO { get; set; }

        
    }
}
