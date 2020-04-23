from flask import render_template
from attendanceproject import app, db
from attendanceproject.forms import *
from flask_login import (login_user, login_required,
                         logout_user, current_user,
                         fresh_login_required)


@app.route('/', methods=["GET"])
@app.route('/home', methods=["GET"])
def home():
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template("register.html", form=form)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/classes')
def classes():
    return render_template("my_classes.html")

@app.route('/classes/<class_code>')
def class_code(class_code):
    return render_template("class.html")

@app.route('/account/<user>')
def account(user):
    return render_template("account.html")
