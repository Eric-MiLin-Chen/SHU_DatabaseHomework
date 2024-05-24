using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WebHomework.Models
{
    [Table("Department")]
    public class Department
    {
        [Key]
        [Column("DepartmentNO")]//系编号
        public string DepartmentNO { get; set; }

        [Column("DepartmentName")]//系名
        public string DepartmentName { get; set; }
    }
}
