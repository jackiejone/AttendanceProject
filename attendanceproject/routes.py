from flask import render_template, request, flash, redirect, url_for
from attendanceproject import app, db
from attendanceproject.forms import *
from attendanceproject.models import *
from flask_login import (login_user, login_required,
                         logout_user, current_user,
                         fresh_login_required)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

@app.route('/', methods=["GET"])
@app.route('/home', methods=["GET"])
def home():
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        fname = form.fname.data.strip().lower()
        lname = form.lname.data.strip().lower()
        email = form.email.data.strip().lower()
        student_code = form.std_code.data.strip().lower()
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User(fname=fname, lname=lname,
                    student_code=student_code, email=email,
                    password=hashed_password)
        try:
            db.session.add(user)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            flash('Email or Student Code Already Taken')
        else:
            db.session.commit()
            flash("Successfully Register")
            return redirect(url_for('login'))
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
