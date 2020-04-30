from flask import render_template, request
from attendanceproject import app, db
from attendanceproject.forms import *
from attendanceproject.models import *
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
    if request.method == "POST" and form.validate_on_submit():
        print('got here first')
        user = User(fname=form.fname.data, lname=form.lname.data,
                    student_code=form.std_code.data, email=form.email.data,
                    password=form.password.data)
        print('got here')
        db.session.add(user)
        db.session.commit()
        return "Added User"
        
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
