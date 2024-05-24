namespace WebHomework.Models
{
    public class StudentCourseViewModel
    {
        public List<StudentCourse> StudentCourse { get; set; }
        public List<Course> Course { get; set; }
        public List<TeacherCourse> TeacherCourse { get; set; }
        public List<Teacher> Teacher { get; set; }
    }
}
