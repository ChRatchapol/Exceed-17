from flask import Flask, render_template, url_for, request, session, make_response, redirect, flash, Markup
from functools import wraps
import datetime
import requests
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = "abcdef"
login_cond = 0

def token_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        header = {"Authorization":f"Bearer {request.cookies.get('token')}"}
        response = requests.get("http://158.108.182.0:3000/", headers=header)
        if response.json()["message"] == "OK":
            return func(*args, **kwargs)
        else:
            flash("login first!", "danger")
            return redirect(url_for("login"))
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        header = {"Authorization":f"Bearer {request.cookies.get('token')}"}
        response = requests.get("http://158.108.182.0:3000/", headers=header)
        if response.json()["group"] == "admin":
            return func(*args, **kwargs)
        else:
            flash("You need to be an admin!", "danger")
            return redirect(url_for("home"))
    return inner

def login_chk():
    header = {"Authorization":f"Bearer {request.cookies.get('token')}"}
    response = requests.get("http://158.108.182.0:3000/", headers=header)
    if response.json()["message"] == "OK":
        login_cond = 1
    else:
        login_cond = 0

    try:
        response.json()["group"]
    except:
        return login_cond, ""
    else:
        return login_cond, response.json()["group"]


@app.route("/")
def home():
    login_cond, group = login_chk()

    now = datetime.datetime.now()
    F6 = datetime.datetime(2021,2,6)
    F7 = datetime.datetime(2021,2,7)
    F13 = datetime.datetime(2021,2,13)
    F14 = datetime.datetime(2021,2,14)
    F20 = datetime.datetime(2021,2,20)
    F21 = datetime.datetime(2021,2,21)
    return render_template("index.html", F6=now>=F6, F7=now>=F7, F13=now>=F13, F14=now>=F14, F20=now>=F20, F21=now>=F21, login=login_cond, group=group)

@app.route("/logout", methods=["GET"])
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie('token', '', httponly=True, expires=0)
    resp.set_cookie('user', '', httponly=False, expires=0)
    flash("logout success!", "success")
    return resp

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", login=2)
    else:
        url = "http://158.108.182.0:3000/login"

        payload = request.form
        usrnm = payload["username"]
        pswd = payload["passwd"]
        credentials = f"{usrnm}:{pswd}"
        cred_bytes = credentials.encode('ascii')
        cred_fin = base64.b64encode(cred_bytes).decode('ascii')
        headers = {"Authorization": f"Basic {cred_fin}"}

        response = requests.request("POST", url, headers=headers, data=payload)

        if (response.status_code == 401):
            flash("login fail!", "danger")
            return render_template("login.html", login=2, group="")
        else:
            json = response.json()
            resp = make_response(redirect("/"))
            resp.set_cookie('token', json["token"], httponly=True)
            resp.set_cookie('user', usrnm, httponly=False)
            flash("login success!", "success")
            return resp


@app.route("/balance", methods=["PUT", "GET"])
@token_required
def balance():
    login_cond, group = login_chk()

    header = {"Authorization":f"Bearer {request.cookies.get('token')}"}
    response = requests.get("http://158.108.182.0:3000/", headers=header)
    if response.json()["group"] == "admin":
        return render_template("balance_admin.html", balance=True, login=login_cond, group=group)
    else:
        return render_template("balance.html", balance=True, login=login_cond, group=group)


@app.route("/price-cal")
@token_required
@admin_required
def price_cal():
    login_cond, group = login_chk()
    return render_template("price-cal.html", price_cal=True, login=login_cond, group=group)


if __name__ == "__main__":
    app.run(debug=True)