
var tested = true;        //测试时设置为true，正式使用时设置为false
var flaskurl = "http://127.0.0.1:5000";
var currentuser;
setInterval(() => {
    currentuser = document.getElementsByClassName("nav-no")[0].innerHTML;
}, 50);

//处理登录
document.getElementById("login-submit").onclick = function () {

    if (tested) { turnStudent(); return; }

    var username = document.getElementById("username").value;
    document.getElementsByClassName("nav-no")[0].innerHTML = username;

    var password = document.getElementById("password").value;
    var data = {
        username: username,
        password: password
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", `${flaskurl}/login/`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(dataStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                turnStudent();
            } else {
                alert("用户名或密码错误！");
            }
        }
    }
}

//处理跳转不同界面
function turnStudent() {
    document.getElementsByClassName("login-frame")[0].style.display = "none";
    document.getElementsByClassName("menu-student")[0].style.display = "block";
    document.getElementsByClassName("main-frame")[0].style.display = "block";
    document.getElementsByClassName("aside-sinfo")[0].style.display = "block";
}

function turnTeacher() {
    document.getElementsByClassName("login-frame")[0].style.display = "none";
    document.getElementsByClassName("menu-teacher")[0].style.display = "block";
    document.getElementsByClassName("main-frame")[0].style.display = "block";
    document.getElementsByClassName("aside-sinfo")[0].style.display = "none";
}

function turnManager() {
    document.getElementsByClassName("login-frame")[0].style.display = "none";
    document.getElementsByClassName("menu-admin")[0].style.display = "block";
    document.getElementsByClassName("main-frame")[0].style.display = "block";
    document.getElementsByClassName("aside-sinfo")[0].style.display = "none";
}

//处理学生操作
function handleChooseArticleItemShow(i) {
    for (let j = 0; j < 3; j++) {
        document.getElementsByClassName("article-item")[j].style.display = "none";
    }
    document.getElementsByClassName("article-item")[i].style.display = "block";
}

document.getElementById("student-select").onclick = function () { handleChooseArticleItemShow(0); }
document.getElementById("student-drop").onclick = function () { handleChooseArticleItemShow(1); }
document.getElementById("student-scheduleInquiry").onclick = function () { handleChooseArticleItemShow(2); }


//处理退出
function logoutHandler() {
    document.getElementsByClassName("main-frame")[0].style.display = "none";
    document.getElementsByClassName("menu-student")[0].style.display = "none";
    document.getElementsByClassName("menu-teacher")[0].style.display = "none";
    document.getElementsByClassName("menu-admin")[0].style.display = "none";
    document.getElementsByClassName("login-frame")[0].style.display = "block";
}

document.getElementsByClassName("nav-logout")[0].onclick = logoutHandler;
document.getElementById("redlogout").onclick = logoutHandler;

//处理点击menu-xxx-title
var menuMasked = false;
function menucontentHandler(user, deltaY) {
    if (!menuMasked) {
        document.getElementsByClassName("menu-mask")[user].style.transform = `translateY(-${deltaY}vh)`;
        menuMasked = true;
    } else {
        document.getElementsByClassName("menu-mask")[user].style.transform = `translateY(0)`;
        menuMasked = false;
    }
}
document.getElementById("menu-student-title").onclick = function () { menucontentHandler(0, 10.5) };
document.getElementById("menu-teacher-title").onclick = function () { menucontentHandler(1, 3.5) };
document.getElementById("menu-admin-title").onclick = function () { menucontentHandler(2, 10.5) };

//测试时加入数据
if (tested) {
    document.getElementById("courseInquiryResult").innerHTML = `
    <tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr><tr>
        <td>1</td>
        <td>2</td>
        <td>3</td>
        <td>4</td>
        <td>5</td>
        <td>6</td>
        <td><button>选课</button></td>
    </tr>`;
}

//处理课程查询
function handleCourseQuery() {
    var courseNo = document.getElementById("courseNo").value;
    var courseName = document.getElementById("courseName").value;
    var teacherNo = document.getElementById("teacherNo").value;
    var teacherName = document.getElementById("teacherName").value;
    var courseTime = document.getElementById("courseTime").value;
    var courseCredit = document.getElementById("courseCredit").value;
    var data = {
        kch: courseNo,
        kcm: courseName,
        xf: courseCredit,
        jsh: teacherNo,
        jsxm: teacherName,
        sksj: courseTime
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", `${flaskurl}/courseQuery/`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(dataStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                var courseInfo = res.data;
                var courseInfoStr = "";
                for (let i = 0; i < courseInfo.length; i++) {
                    courseInfoStr += `<tr>
                    <td>${courseInfo[i].kch}</td>
                    <td>${courseInfo[i].kcm}</td>
                    <td>${courseInfo[i].xf}</td>
                    <td>${courseInfo[i].jsh}</td>
                    <td>${courseInfo[i].jsxm}</td>
                    <td>${courseInfo[i].sksj}</td>
                    <td><button class="selectCourseButton">选课</button></td>
                    </tr>`;
                    document.getElementsByClassName("selectCourseButton")[i].onclick = function () {
                        handleSelectCourse(currentuser, courseInfo[i].kch);
                    }
                }
                document.getElementById("courseInquiryResult").innerHTML = courseInfoStr;
            } else {
                alert("查询失败！");
            }
        }
    }
}
document.getElementById("courseInquiry").onclick = handleCourseQuery;

//处理选课
function handleSelectCourse(user, kch) {
    var data = {
        username: user,
        kch: kch
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", `${flaskurl}/selectCourse/`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(dataStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                alert("选课成功！");
            } else {
                alert("选课失败！");
            }
        }
    }
}