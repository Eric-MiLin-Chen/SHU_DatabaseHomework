
document.getElementById("login-submit").onclick = function () {
    var username = document.getElementById("username").value;
    document.getElementsByClassName("nav-no")[0].innerHTML = username;
    var password = document.getElementById("password").value;
    var data = {
        username: username,
        password: password
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/login/", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(dataStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            var res = xhr.responseText;
            if (res == "success") {
                document.getElementsByClassName("login-frame")[0].style.display = "none";
                document.getElementsByClassName("semester-frame")[0].style.display = "block";
            } else {
                alert("用户名或密码错误！");
            }
        }
    }
}

document.getElementById("semester-submit").onclick = function () {
    var semester = document.getElementById("semester").value;
    if (semester == "") {
        document.getElementsByClassName("semester-frame")[0].style.display = "none";
        document.getElementsByClassName("main-frame")[0].style.display = "block";
        return;
    }
    var data = {
        semester: semester
    };
    var dataStr = JSON.stringify(data);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/semester", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(dataStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var res = JSON.parse(xhr.responseText);
            if (res.status == "success") {
                window.location.href = "/courseSelectionSystem/html/index.html";
            } else {
                alert("学期不存在！");
            }
        }
    }
}

function logoutHandler() {
    document.getElementsByClassName("main-frame")[0].style.display = "none";
    document.getElementsByClassName("semester-frame")[0].style.display = "none";
    document.getElementsByClassName("menu-student")[0].style.display = "none";
    document.getElementsByClassName("menu-teacher")[0].style.display = "none";
    document.getElementsByClassName("menu-admin")[0].style.display = "none";
    document.getElementsByClassName("login-frame")[0].style.display = "block";
}

document.getElementsByClassName("nav-logout")[0].onclick=logoutHandler;
document.getElementById("redlogout").onclick=logoutHandler;


var menuMasked = false;
function menucontentHandler(user,deltaY) {
    if (!menuMasked) {
        document.getElementsByClassName("menu-mask")[user].style.transform = `translateY(-${deltaY}vh)`;
        menuMasked = true;
    } else {
        document.getElementsByClassName("menu-mask")[user].style.transform = `translateY(0)`;
        menuMasked = false;
    }
}
document.getElementById("menu-student-title").onclick = function () { menucontentHandler(0,10.5) };
document.getElementById("menu-teacher-title").onclick = function () { menucontentHandler(1,3.5) };
document.getElementById("menu-admin-title").onclick = function () { menucontentHandler(2,10.5) };
