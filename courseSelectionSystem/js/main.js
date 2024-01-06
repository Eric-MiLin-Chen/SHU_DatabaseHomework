
var tested = false;        //测试时设置为true，正式使用时设置为false
var flaskurl = "http://127.0.0.1:5001";
var currentuser;
setInterval(() => {
    currentuser = document.getElementsByClassName("nav-no")[0].innerHTML;
}, 50);
var Authorization;

//处理登录
document.getElementById("login-submit").onclick = function () {

    if (tested) { turnStudent(); return; }

    var username = document.getElementById("username").value;
    document.getElementsByClassName("nav-no")[0].innerHTML = username;

    var password = document.getElementById("password").value;
    var data = {
        login_info: {
            username: username,
            password: password
        }
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
                Authorization = res.Authorization;
                document.getElementById("sname").innerHTML = res.user_info.name;
                document.getElementById("sschool").innerHTML = res.user_info.school;
                document.getElementById("sgrade").innerHTML = res.user_info.level;
                document.getElementById("ssex").innerHTML = res.user_info.gender;
                turnStudent();
            } else {
                alert(res.message);
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
document.getElementById("student-drop").onclick = function () { handleChooseArticleItemShow(1); handleCurrentCourseQuery(); }
document.getElementById("student-scheduleInquiry").onclick = function () { handleChooseArticleItemShow(2); handleScheduleQuery(); }


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


//处理选课课程查询
function handleCourseQuery() {
    var courseNo = document.getElementById("courseNo").value;
    var courseName = document.getElementById("courseName").value;
    var teacherNo = document.getElementById("teacherNo").value;
    var teacherName = document.getElementById("teacherName").value;
    var courseTime = document.getElementById("courseTime").value;
    var courseCredit = document.getElementById("courseCredit").value;
    var data = {
        course_info: {
            kch: courseNo,
            kcm: courseName,
            xf: courseCredit,
            jsh: teacherNo,
            jsxm: teacherName,
            sksj: courseTime
        },
        action: "get_schedule",
        Authorization: Authorization
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    if (tested) { xhr.open("get", "test.json"); }
    else { xhr.open("POST", `${flaskurl}/student_enroll/`, true); }
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", Authorization);
    if (tested) { xhr.send(null); }
    else { xhr.send(dataStr); }
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                var courseInfo = res.course_info;
                // console.log(courseInfo);
                for (let i = 0; i < courseInfo.length; i++) {
                    let newtr = document.createElement("tr");
                    let newtd0 = document.createElement("td");
                    newtd0.innerHTML = courseInfo[i].kch;
                    let newtd1 = document.createElement("td");
                    newtd1.innerHTML = courseInfo[i].kcm;
                    let newtd2 = document.createElement("td");
                    newtd2.innerHTML = courseInfo[i].xf;
                    let newtd3 = document.createElement("td");
                    newtd3.innerHTML = courseInfo[i].jsh;
                    let newtd4 = document.createElement("td");
                    newtd4.innerHTML = courseInfo[i].jsxm;
                    let newtd5 = document.createElement("td");
                    newtd5.innerHTML = courseInfo[i].sksj;
                    let newtd6 = document.createElement("td");
                    let newbutton = document.createElement("button");
                    newbutton.innerHTML = "选课";
                    newbutton.onclick = function () {
                        handleSelectCourse(courseInfo[i].kch, courseInfo[i].jsh, "enroll");
                    }
                    newtd6.appendChild(newbutton);
                    newtr.appendChild(newtd0);
                    newtr.appendChild(newtd1);
                    newtr.appendChild(newtd2);
                    newtr.appendChild(newtd3);
                    newtr.appendChild(newtd4);
                    newtr.appendChild(newtd5);
                    newtr.appendChild(newtd6);
                    document.getElementById("courseInquiryResult").appendChild(newtr);
                }
            } else {
                alert(res.message);
            }
        }
    }
}
document.getElementById("courseInquiry").onclick = handleCourseQuery;


//处理当前课程查询
function handleCurrentCourseQuery() {
    var data = {
        action: "get_schedule",
        Authorization: Authorization
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    if (tested) { xhr.open("get", "test.json"); }
    else { xhr.open("POST", `${flaskurl}/get_schedule/`, true); }
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", Authorization);
    if (tested) { xhr.send(null); }
    else { xhr.send(dataStr); }
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                var courseInfo = res.course_info;
                for (let i = 0; i < courseInfo.length; i++) {

                    let newtr = document.createElement("tr");
                    let newtd0 = document.createElement("td");
                    newtd0.innerHTML = courseInfo[i].kch;
                    let newtd1 = document.createElement("td");
                    newtd1.innerHTML = courseInfo[i].kcm;
                    let newtd2 = document.createElement("td");
                    newtd2.innerHTML = courseInfo[i].xf;
                    let newtd3 = document.createElement("td");
                    newtd3.innerHTML = courseInfo[i].jsh;
                    let newtd4 = document.createElement("td");
                    newtd4.innerHTML = courseInfo[i].jsxm;
                    let newtd5 = document.createElement("td");
                    newtd5.innerHTML = courseInfo[i].sksj;
                    let newtd6 = document.createElement("td");
                    let newbutton = document.createElement("button");
                    newbutton.innerHTML = "退课";
                    newbutton.onclick = function () {
                        handleSelectCourse(courseInfo[i].kch, courseInfo[i].jsh, "drop");
                    }
                    newtd6.appendChild(newbutton);
                    newtr.appendChild(newtd0);
                    newtr.appendChild(newtd1);
                    newtr.appendChild(newtd2);
                    newtr.appendChild(newtd3);
                    newtr.appendChild(newtd4);
                    newtr.appendChild(newtd5);
                    newtr.appendChild(newtd6);
                    document.getElementById("currentSelectedResult").appendChild(newtr);
                }
            } else {
                alert(res.message);
            }
        }
    }
}


//处理课程变动
function handleSelectCourse(kch, jsh, action) {
    var data = {
        course_info: {
            kch: kch,
            jsh: jsh
        },
        action: action,
        Authorization: Authorization
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    if (action == "enroll") {
        xhr.open("POST", `${flaskurl}/student_enroll/`, true);
    }
    if (action == "drop") {
        xhr.open("POST", `${flaskurl}/drop_course/`, true);
    }
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", Authorization);
    xhr.send(dataStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                if (action == "enroll") {
                    alert("选课成功！");
                }
                if (action == "drop") {
                    alert("退课成功！");
                }
            } else {
                alert(res.message);
            }
        }
    }
}

//处理课程表查询
var xuhao = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
var week = ["一", "二", "三", "四", "五"];
function handleScheduleQuery() {
    var data = {
        action: "get_schedule",
        Authorization: Authorization
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    if (tested) { xhr.open("get", "test.json"); }
    else { xhr.open("POST", `${flaskurl}/get_schedule/`, true); }
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", Authorization);
    if (tested) { xhr.send(null); }
    else { xhr.send(dataStr); }
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                var courseInfo = res.course_info;
                var courseInfoStr = "";
                for (let i = 0; i < courseInfo.length; i++) {
                    courseInfoStr += `<tr>
                    <td>${xuhao[i]}</td>
                    <td>${courseInfo[i].kch}</td>
                    <td>${courseInfo[i].kcm}</td>
                    <td>${courseInfo[i].xf}</td>
                    <td>${courseInfo[i].jsh}</td>
                    <td>${courseInfo[i].jsxm}</td>
                    <td>${courseInfo[i].sksj}</td>
                    </tr>`;
                    for (let j = 0; j < 5; j++) {
                        if (courseInfo[i].sksj[0] == week[j]) {
                            let str = courseInfo[i].sksj.slice(1);
                            let pos = str.indexOf("-");
                            let start = Number(str.slice(0, pos));
                            let end = Number(str.slice(pos + 1));
                            let leg = end - start + 1;
                            for (let k = 0; k < leg; k++) {
                                document.getElementsByClassName("schedule-item")[j + (start - 1 + k) * 5].innerHTML = xuhao[i];
                            }
                        }
                    }
                }
                document.getElementById("currentSelectedResult2").innerHTML = courseInfoStr;
            } else {
                alert(res.message);
            }
        }
    }
}


if (tested) {
    var courseInfo = [
        {
            sksj: "一1-2"
        },
        {
            sksj: "二1-2"
        },
        {
            sksj: "三1-2"
        },
        {
            sksj: "三11-12"
        },
        {
            sksj: "五1-2"
        },
        {
            sksj: "一3-4"
        },
        {
            sksj: "二3-4"
        },
        {
            sksj: "三3-4"
        },
        {
            sksj: "四3-4"
        }
    ];
    for (let i = 0; i < courseInfo.length; i++) {
        for (let j = 0; j < 5; j++) {
            if (courseInfo[i].sksj[0] == week[j]) {
                let str = courseInfo[i].sksj.slice(1);
                let pos = str.indexOf("-");
                let start = Number(str.slice(0, pos));
                let end = Number(str.slice(pos + 1));
                let leg = end - start + 1;
                for (let k = 0; k < leg; k++) {
                    document.getElementsByClassName("schedule-item")[j + (start - 1 + k) * 5].innerHTML = xuhao[i];
                }
            }
        }
    }
}