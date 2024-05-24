using Microsoft.EntityFrameworkCore;
using WebHomework.Models;

namespace WebHomework.Data
{
    public class WebHomeworkContext : DbContext
    {
        public WebHomeworkContext (DbContextOptions<WebHomeworkContext> options)
            : base(options)
        {
        }

        public DbSet<WebHomework.Models.Password> Password { get; set; } = default!;
        public DbSet<WebHomework.Models.Teacher> Teacher { get; set; } = default!;
        public DbSet<WebHomework.Models.Department> Department { get; set; } = default!;
        public DbSet<WebHomework.Models.TeacherCourse> TeacherCourse { get; set; } = default!;
        public DbSet<WebHomework.Models.Course> Course { get; set; } = default!;
        public DbSet<WebHomework.Models.Student> Student { get; set; } = default!;
        public DbSet<WebHomework.Models.StudentCourse> StudentCourse { get; set; } = default!;

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<TeacherCourse>()
                .HasKey(tc => new { tc.TeacherNO, tc.CourseNO });

            modelBuilder.Entity<StudentCourse>()
                .HasKey(sc => new { sc.StudentNO, sc.CourseNO });

            base.OnModelCreating(modelBuilder);
        }
    }
}
