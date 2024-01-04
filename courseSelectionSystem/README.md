# 数据库大作业手册

## 前端需求

1. 登录界面：
   1. 学生用户
      1. 选课/课程查询界面
      2. 退课界面
      3. 课表查询
   2. 教师用户
      1. 课表查询
   3. 管理员用户
      1. 增删查改课程（包括课程容量/锁课？）
      2. 增删查改学生、教师
      3. 增删查改学生选择课程
      4. 修改课程最大人数

## 数据库需求

1. 学生库S
   学号、姓名、在读年级、性别、学院号
2. 课程库C
   课程号、学院号、课程名、学分、最大人数、上课时间、教师工号
3. 教师库T
   教师工号、教师姓名、教师职称、性别、学院号
4. 学院库I
   学院号、学院名称
5. 课表库E
   学号、课程号、教师工号
6. 密码库P

   学/工号、密码

### 前后端json格式

| 超属性        | 属性     | 内容类型 | 内容                        | 描述           |
| ------------- | -------- | -------- | --------------------------- | -------------- |
| login_info    | username | char     |                             |                |
|               | password | char     |                             |                |
| status        |          | char     | success\|failed             |                |
| user_info     | status   | int      | 用户身份（0学生1老师2管理） |                |
|               | id       | char     | 学/工号                     |                |
|               | gender   | char     | 性别                        |                |
|               | college  | char     | 学院                        |                |
| Authorization |          | char     | 认证密钥，判断请求是否合法  | Request Header |
| action        |          | char     | enroll\|drop\|get_schedule  | 选/退/查       |
| total_count   |          | int      |                             | 查询的课程总数 |
| course_info   | kch      | char     |                             | 查询：课程号   |
|               | kcm      | char     |                             | 查询：课程名   |
|               | xf       | char     |                             | 查询：学分     |
|               | jsh      | char     |                             | 查询：教师号   |
|               | jsxm     | char     |                             | 查询：教师姓名 |
|               | sksj     | char     |                             | 查询：上课时间 |
| message       |          | char     |                             | 报错信息       |

### 后端

#### API

**登录界面：**

   请求：

   ```json
   {
      "login_info": {
         "username": "",
         "password": "",
      }
   }

   ```

   返回：

   ```json
   // 失败
   {
      "status": "failed",
      "message": "",
   }
   // 所有请求失败返回都如上，以下不再重复（包括身份认证）

   // 成功
   {
      "status": "success",
      "Authorization": "",
      "user_info": {
         "username": "",// 学号/工号
         "name": "",    // 姓名，管理员"name": "admin"
         "school": "",
         "level": "",
         "gender": "",
         "role": "",    // 用户类型/权限等级
      },
   }
   // 后续Authorization作为请求头，不会明确写入发送端要求
   // 除了登录外每次请求都有身份验证
   ```

1. 学生用户
   1. 选课/课程查询界面

   请求：

   ```json
   // get_schedule
   {
      "action": "get_schedule",
      "course_info": {
         "kch": "",
         "kcm": "",
         "xf": "",
         "jsh": "",
         "jsxm": "",
         "sksj": "",
         // 没有选择也必须要有
      }, 
   }

   // enroll
   {
      "action": "enroll",
      "course_info": {
         "kch": "",
         "jsh": "",
         // "kcm": "",
         // "xf": "",
         // "jsxm": "",
         // "sksj": "",
      }, 
   }
   ```

   返回：

   ```json
   // 成功
   // 课程查询请求
   {
      "total_count": (int),
      "course_info": [
         {
            {
               "kch": "",
               "kcm": "",
               "xf": "",
               "jsh": "",
               "jsxm": "",
               "sksj": "",
               "zdrs": "",
            }, 
         },
         // ...
      ],
      "status": "success",
   }

   // 选课请求
   {
      "status": "success",
   }
   ```

   2. 退课界面

   请求：

   ```json
   // get_schedule时不检查course_info
   {
      "action": "get_schedule",
   }

   // drop
   {
      "action": "drop",
      // get_schedule时不检查course_info
      "course_info": {
         "kch": "",
         "kcm": "",
         // "xf": "",
         // "jsh": "",
         // "jsxm": "",
         // "sksj": "",
         // "zdrs": "",
      }, 
   }
   ```

   返回：

   ```json
   // get_schedule
   {
      "status": "success",
      "total_count": (int),
      "course_info": [
         {
            "kch": "",
            "kcm": "",
            "xf": "",
            "jsh": "",
            "jsxm": "",
            "sksj": "",
            "zdrs": "",
         },
      ], 
   }

   // drop
   {
      "status": "success",
   }
   ```

   3. 课表查询
   
   请求：

   ```json
   // get_schedule时不检查course_info
   {
      "action": "get_schedule",
   }
   ```

   返回：

   ```json
   // get_schedule
   {
      "status": "success",
      "total_count": (int),
      "course_info": [
         {
            "kch": "",
            "kcm": "",
            "xf": "",
            "jsh": "",
            "jsxm": "",
            "sksj": "",
            "zdrs": "",
         },
      ], 
   }
   ```

2. 教师用户
   1. 课表查询
3. 管理员用户
   1. 增删查改课程（包括课程容量/锁课？）
   2. 增删查改学生、教师
   3. 增删查改学生选择课程
   4. 修改课程最大人数
