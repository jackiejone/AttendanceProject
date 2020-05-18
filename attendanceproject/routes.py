from flask import render_template, request, flash, redirect, url_for
from attendanceproject import app, db
from attendanceproject.forms import *
from attendanceproject.models import *
from flask_login import (login_user, login_required,
                         logout_user, current_user,
                         fresh_login_required)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from string import ascii_letters, digits
from random import choice


# Home Route
@app.route('/', methods=["GET"])
@app.route('/home', methods=["GET"])
def home():
    return render_template("home.html")

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm() # Getting register form
    
    # Checking for POST request and form validation
    if request.method == "POST" and form.validate_on_submit():
        # Formatting first name, last name, email, and student number to prevent errors
        fname = form.fname.data.capitalize().strip().lower()
        lname = form.lname.data.capitalize().strip().lower()
        email = form.email.data.strip().lower()
        student_code = form.std_code.data.strip().lower()
        # Generates hashed password using SHA256 encryption method
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        # Defines new user object to add to database
        user = User(fname=fname, lname=lname,
                    student_code=student_code, email=email,
                    password=hashed_password)
        # Error checking to check if the user already exsists in the database
        try:
            db.session.add(user)
            db.session.flush()
        except IntegrityError: # IntegrityError occurs when unique constraint is failed
            db.session.rollback()
            flash('Email or Student Code Already Taken')
        else:
            db.session.commit()
            flash("Successfully Register")
            return redirect(url_for('login'))
    return render_template("register.html", form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() # Getting login form
    
    # Checks for post request and validates form
    if request.method == 'POST' and form.validate_on_submit():
        # Formats email address to same format in database
        email = form.email.data.strip().lower()
        # Searches database for user with the same email
        user = User.query.filter_by(email=email).first()
        # Checks if the user exists
        if user:
            # Checks the hashed password with the password from the form
            if check_password_hash(user.password, form.password.data):
                # log in the user and go to the page they we're redirected from or take them to the home page
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Invalid Email or Password')
        else:
            flash('Invalid Email or Password')
    return render_template("login.html", form=form)

# Logout Route
@app.route('/logout')
def logout():
    # Check if the user is logged in
    if current_user.is_authenticated:
        # Logs out the user
        logout_user()
    # Redirects the user to the home page
    return redirect(url_for('home'))

# Classes Route
@app.route('/classes')
@login_required
def classes():
    return render_template("my_classes.html")

def generate_code():
    chars = ascii_letters + digits
    code = ''.join(choice(chars) for i in range(6))
    if SubjectCode.query.filter_by(join_code=code).first():
        generate_code()
    else:
        return code

@app.route('/new_class', methods=['GET', 'POST'])
@login_required
def create_class():
    form = CreateClassForm()
    if current_user.auth != "teacher":
        flash("You do not have permission to access this page")
        return redirect(url_for('home'))
    if request.method == 'POST' and form.validate_on_submit():
        class_name = form.cname.data.capitalize().strip().lower()
        class_code = form.ccode.data
        join_code = generate_code()
        new_class = SubjectCode(name=class_name, code=class_code,
                                join_code=join_code)
        try:
            db.session.add(new_class)
            db.session.flush()
        except IntegrityError:
            flash('Class Code Already Taken')
        else:
            db.session.commit()
            flash('Class Successfully Added')
            user = User.query.filter_by(id=current_user.id).first()
            asso = UserSubject(user_type='teacher')
            asso.subject = new_class
            user.subjects.append(asso)
            db.session.commit()
    return render_template('create_class.html', form=form)

# Individual class route
@app.route('/classes/<class_code>')
@login_required
def class_code(class_code):
    return render_template("class.html")

# Account Route
@app.route('/account/<user>')
@login_required
def account(user):
    return render_template("account.html")
