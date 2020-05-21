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
@app.route('/classes', methods=['GET', 'POST'])
@login_required
def classes():
    # Dynamically creating booleanfields for each class
    classes = SubjectCode.query.all()
    sclasses = [(x.id, x.name) for x in classes]
    form = JoinClassForm()
    form.classes.choices = sclasses
    print(form.classes)
    # Handling form post reqeust for adding a user to multiple classes
    if request.method == 'POST' and form.validate_on_submit():
        formdata = form.classes.data
        # Stopping user to join class if they already have 6 classes or amount
        # of choices exceede maxmium of 6 classes
        if (UserSubject.query.filter_by(user_id=current_user.id).count() > 6
            or len(formdata) > 6
            or len(formdata) + UserSubject.query.filter_by(user_id=current_user.id).count() > 6):
            flash('Maximium classes a user can have is 6') # FIX STATEMENT SO IT IGNORES CLASSES ALREADY JOINED
            return render_template('my_classes.html', form=form, formdata=None)
        
        else:
            for sub_id in formdata:
                add_user_subject = UserSubject(user_id=current_user.id, subject_id=sub_id, user_type=current_user.auth)
                user_subjects = UserSubject.query.filter_by(user_id=current_user.id, subject_id=sub_id).first()
                if user_subjects:
                    continue
                else:
                    try:
                        db.session.add(add_user_subject)
                        db.session.flush()
                    except:
                        db.session.rollback()
                    else:
                        db.session.commit()
            return render_template('my_classes.html', form=form, formdata=formdata)
    return render_template('my_classes.html', form=form, formdata=None)

# Function to create unique alphanumeric codes
def generate_code():
    # Defines the list of imported characters to be chosen from
    chars = ascii_letters + digits
    # Creates string with 6 randomly chosen characters linked together
    code = ''.join(choice(chars) for i in range(6))
    # Checks if the code already exists in the database
    # generates a new code if the code already exists
    if SubjectCode.query.filter_by(join_code=code).first():
        generate_code()
    else:
        return code

# Route for creating new class
@app.route('/new_class', methods=['GET', 'POST'])
@login_required
def create_class():
    form = CreateClassForm()
    # Checking if the user accessing the page is a teacher
    if current_user.auth != "teacher":
        flash("You do not have permission to access this page")
        # Redirects the user back to the home page if they're not a teacher
        return redirect(url_for('home'))
    
    # Checks for POST request and valid form
    if request.method == 'POST' and form.validate_on_submit():
        # Prepares form data For insertion into database
        class_name = form.cname.data.capitalize().strip().lower()
        class_code = form.ccode.data
        join_code = generate_code()
        # Creates new class object with data from the form
        new_class = SubjectCode(name=class_name, code=class_code,
                                join_code=join_code)
        # Tries to add the new class to the database and flues it
        # If an IntegrityError is returned, then the class already exists and 
        # no new class is added to the database
        try:
            db.session.add(new_class)
            db.session.flush()
        except IntegrityError:
            flash('Class Code Already Taken')
        else:
            # If there is no error returned, the class is added to the database and
            # the teacher who created the class is also associated with the class
            db.session.commit()
            flash('Class Successfully Added')
            # Associating the teacher with the class
            if form.auto_add.data == True:
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
