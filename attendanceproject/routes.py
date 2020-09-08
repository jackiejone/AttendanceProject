from flask import render_template, request, flash, redirect, url_for
from attendanceproject import app, db
from attendanceproject.forms import *
from attendanceproject.models import *
from flask_login import (login_user, login_required,
                         logout_user, current_user,
                         fresh_login_required)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from string import ascii_letters, digits
from random import choice
import datetime
from math import ceil


CONSTANT_DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') 

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
        user_code = form.std_code.data.strip().lower()
        # Generates hashed password using SHA256 encryption method
        hashed_password = generate_password_hash(form.password.data, method='sha256', salt_length=10)
        # Defines new user object to add to database
        user = User(fname=fname, lname=lname,
                    user_code=user_code, email=email,
                    password=hashed_password, auth='student')
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
        flash('Successfully Logged out')
    # Redirects the user to the home page
    return redirect(url_for('home'))

# Function for putting the name of the user's subjects into a list
def subject_name(user):
    return [x.subject for x in user.subjects]

def populate_JoinClassForm(user):
    # Dynamically creating booleanfields for each class
    classes = SubjectCode.query.all()
    # Excluding classes for which the user is already in
    sclasses = [(x.id, x.name) for x in classes if x.id not in [y.subject_id for y in user.subjects]]
    form = JoinClassForm()
    if sclasses:
        form.classes.choices = sclasses
    return form

# Function to check if a user is trying to join a class/subject which has conlficting time/s with one of their other classes/subjects
def check_conflicting_times(user, subject_id):
    if type(subject_id) == int:
        subject = SubjectCode.query.filter_by(id=subject_id).first()
    else:
        subject = SubjectCode.query.filter_by(join_code=subject_id).first()
    
    if not subject.times:
        return False
    for times in subject.times:
        sub_times = SubjectTimes.query.filter_by(stime_id=times.stime_id, sweek=times.sweek, sday=times.sday).all()
        if len(sub_times) > 1:
            for i in sub_times:
                for x in i.subject.users:
                    if user.id == x.user_id:
                        return True
    return False

# This function returns the nth day of the year
def day_num():
    return datetime.date.today().timetuple().tm_yday

# Classes Route
@app.route('/account/<user_code>/classes', methods=['GET', 'POST'])
@login_required
def classes(user_code):
    # Distingusts between different types of users, teachers and students to
    # present different functions to each party
    if current_user.auth in ['teacher', 'admin']:
        user = User.query.filter_by(user_code=user_code).first()
        if not user:
            flash('User not found')
            return redirect(url_for('classes', user_code=current_user.user_code))
        else:
            user_classes = subject_name(user) # Getting a list of the user's subjects
        # Display and validation of form for adding a user to a class if the user is a teacher
        form = populate_JoinClassForm(user)

        # Handling form post reqeust for adding a user to multiple classes
        if request.method == 'POST' and form.validate_on_submit():
            user = User.query.filter_by(user_code=user_code).first()
            formdata = form.classes.data
            # Stopping user to join class if they already have 6 classes or amount
            # of choices exceede maxmium of 6 classes
            if (len(user.subjects) > 6
                or len(formdata) + UserSubject.query.filter_by(user_id=user.id).count() > 6):
                flash('''Maximium classes a user can have is 6, the amount of classes you have have selected
                to enrol the user into causes the user to exceede the maxmium amount of classes''')
                return render_template('my_classes.html', form=form, formdata=None, user=user, user_classes=user_classes)
            else:
                # Adds the user to the classes based on the selected fields from the form
                conflict_check = False
                for sub_id in formdata:
                    if check_conflicting_times(user, sub_id):
                        if not conflict_check:
                            flash('The class you are trying to join has a conflicting time with one of your other classes')
                            conflict_check = True
                        continue
                    add_user_subject = UserSubject(user_id=user.id, subject_id=sub_id, user_type=user.auth)
                    # Checks if the user is already assocated with the class by
                    # querying the database table with filtered with the user's id and the subject's id
                    user_subjects = UserSubject.query.filter_by(user_id=user.id, subject_id=sub_id).first()
                    if user_subjects:
                        continue
                    else:
                        try:
                            db.session.add(add_user_subject)
                            db.session.flush()
                        except IntegrityError:
                            db.session.rollback()
                        else:
                            db.session.commit()
                            # Refresh user affter change in database
                            user = User.query.filter_by(user_code=user_code).first()
                            form = populate_JoinClassForm(user)
        user_classes = subject_name(user) # Getting a list of the user's subjects/classes
        return render_template('my_classes.html', form=form, user=user, user_classes=user_classes, day_num=day_num())

    else: # If the current user is not a teacher 
        if user_code != current_user.user_code:
            flash("You cannot access this page")
            return redirect(url_for('classes', user_code=current_user.user_code))
        # Display and validation of form if the user is not a teacher, a student
        form = CodeJoinForm()
        if request.method == 'POST' and form.validate_on_submit():
            # Queries the database for the subject based on the join code that
            # was entered into the form
            join_class = SubjectCode.query.filter_by(join_code=form.code.data.strip()).first()
            # Checks if the class exists by checking if there is data returned from the database
            if join_class:
                #  Checks if the user is already associated with the suject/in the subject(in the class)
                if join_class.id in [x.subject_id for x in current_user.subjects]:
                    flash('You have already joined this class')
                # Associating the user with the class
                elif check_conflicting_times(current_user, form.code.data.strip()):
                    flash('The class you are trying to join has a conflicting time with one of your other classes')
                    user_classes = subject_name(current_user) # Getting a list of the user's subjects/classes
                    return render_template('my_classes.html', form=form, user=current_user, user_classes=user_classes, day_num=day_num())
                else:
                    add_user_subject = UserSubject(user_id=current_user.id,
                                                subject_id=join_class.id,
                                                user_type=current_user.auth)
                    try:
                        db.session.add(add_user_subject)
                        db.session.flush()
                    except IntegrityError:
                        flash('Could not join the class')
                    else:
                        db.session.commit()
                        flash('Successfully joined class')
            else:
                flash('Invalid Join Code')
        user_classes = subject_name(current_user) # Getting a list of the user's subjects/classes
        return render_template('my_classes.html', form=form, user=current_user, user_classes=user_classes, day_num=day_num())

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
    # Checking if the user accessing the page is a teacher
    if current_user.auth not in ['teacher', 'admin']:
        flash("You do not have permission to access this page")
        # Redirects the user back to the home page if they're not a teacher
        return redirect(url_for('home'))
    
    form = CreateClassForm()
    # Checks for POST request and valid form
    if request.method == 'POST' and form.validate_on_submit():
        # Prepares form data For insertion into database
        class_name = form.cname.data.capitalize().strip().lower()
        class_code = form.ccode.data.strip().upper()
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
            db.session.rollback()
        else:
            # If there is no error returned, the class is added to the database and
            # the teacher who created the class is also associated with the class
            db.session.commit()
            flash('Class Successfully Added')
            # Associating the teacher with the class
            if form.auto_add.data:
                if len(current_user.subjects) >= 6:
                    flash("Maxmium number of classes reached. You were not added to the class")
                else:
                    user = User.query.filter_by(id=current_user.id).first()
                    asso = UserSubject(user_type='teacher')
                    asso.subject = new_class
                    user.subjects.append(asso)
                    db.session.commit()

    return render_template('create_class.html', form=form)

# Route for viewing all classes/subjects
@app.route('/classes')
@login_required
def all_classes():
    # Checking if the user is a teacher
    if current_user.auth not in ['teacher', 'admin']:
        flash('You do not have access to this page')
        return redirect(url_for('home'))
    # Getting all the classes/subjects form the database
    classes = SubjectCode.query.all()
    return render_template('classes.html', classes=classes)

# Route for viewing a specific subject but not as a particular user
@app.route('/classes/<subject>')
@login_required
def view_subject(subject):
    # Checking if the user is a teacher
    if current_user.auth not in ['teacher', 'admin']:
        flash('You do not have access to this page')
        return redirect(url_for('home'))
    # getting the class/subject from the database
    sub = SubjectCode.query.filter_by(code=subject).first()
    if sub:
        return render_template('class.html', subject=sub, days=CONSTANT_DAYS)
    else:
        flash('Class could not be found')
        return redirect(url_for('all_classes'))

# This function returns the number of days until the first monday of the year
def first_monday():
    for i in range(0, 366):
        start_date = datetime.date(year=datetime.datetime.today().year, month=1, day=1)
        end_date = start_date + datetime.timedelta(days=i)
        if end_date.timetuple().tm_wday == 0:
            return i

# This function checks if the a subject is on a particular date
def check_class_date(subject_date, subject):
    AB = 1
    for i in range(1 + first_monday(), 366):
        date = datetime.timedelta(days=i)
        start_date = datetime.date(2019, 12, 31)
        end_date = start_date + date
        for y in subject.times:
            if end_date.isoweekday()-1 == y.sday and AB == y.sweek and end_date == subject_date:
                print(end_date.isoweekday(), y.sday)
                return {'subject':y, 'day':y.sday, 'week':y.sweek} 
        AB = not AB if end_date.isoweekday() == 5 else AB
    return False

# Function to get all the dates which a class/subject lands on
def get_class_dates(subject):
    subject_dates = []
    AB = 1
    for i in range(1 + first_monday(), 366):
        date = datetime.timedelta(days=i)
        start_date = datetime.date(2019, 12, 31)
        end_date = start_date + date
        for y in subject.times:
            if end_date.isoweekday()-1 == y.sday and AB == y.sweek:
                subject_dates.append((end_date.strftime('%d/%m/%y'), CONSTANT_DAYS[y.sday], 'Week A' if not y.sweek else 'Week B', y.time.start_time))
        AB = not AB if end_date.isoweekday() == 5 else AB
    return subject_dates
 
# Function to return the week of the year
def current_week(viewing_date=datetime.date.today()):
    return 'B' if (ceil((viewing_date.timetuple().tm_yday - first_monday())/7))%2 else 'A'

# Route for viewing a subject/class for a specific user as a specfic user
# This route is split up into three main sections for handling 3 different situations
# The first situation is when a teacher is viewing one of their own classes/subjects
# The second situation is when a teacher is viewing a class with the data of a particular student
# The last siutation is when a student is viewing one of their classes
@app.route('/account/<user_code>/classes/<class_code>/<int:day>', methods=["GET", "POST"])
@login_required
def class_code(class_code, user_code, day):
    subject = SubjectCode.query.filter_by(code=class_code).first()
    prev_next = {'next_day':url_for('class_code', class_code=class_code, user_code=user_code, day=day+1),
                 'prev_day':url_for('class_code', class_code=class_code, user_code=user_code, day=day-1),
                 'today':url_for('class_code', class_code=class_code, user_code=user_code, day=datetime.date.today().timetuple().tm_yday)}
    if not subject:
        flash('Class could not be found')
        return redirect(url_for('classes', user_code=current_user.user_code))
    user = User.query.filter_by(user_code=user_code).first()
    if user:
        total_days = day_num() - day
        current_date = datetime.date.today() - datetime.timedelta(days=total_days)
        # For this one, show the attendane of each student in the class on a certain day
        if (current_user.auth in ['teacher', 'admin'] and class_code in
            [x.subject.code for x in current_user.subjects]) and user == current_user:

            # Getting the date of which the user is viewing via the "day" parameter in the link
            check = check_class_date(subject_date=current_date, subject=subject)
            student_times = [] # Variable for the times of the students in the class
            students_in_class = 0 # Variable used to check if there are students in the class
            if 'student' in [user.user_type for user in subject.users]:
                students_in_class = 1
                # Getting the attendance status of each student in the class for a specific date
                for user in subject.users:
                    added_time = False
                    if user.user_type == 'student':
                        if user.user.attnd_times:
                            for t in user.user.attnd_times:
                                if t.time.date() == current_date and t.subject == subject.id:
                                    student_times.append((user.user, t.attnd_status))
                                    added_time = True
                                    break
                            if not added_time:
                                student_times.append((user.user, "N/A"))
                        else:
                            student_times.append((user.user, "N/A"))
            if check:
                return render_template("teacherclass.html", day_num=day_num(), subject=subject, user=current_user, days=CONSTANT_DAYS, students_in_class=students_in_class, current_date=current_date.strftime('%d/%m/%y'), student_times=student_times, time=check, week=current_week(current_date), day=CONSTANT_DAYS[current_date.isoweekday()-1], prev_next=prev_next, viewing_day=day)
            return render_template("teacherclass.html", day_num=day_num(), subject=subject, user=current_user, days=CONSTANT_DAYS, students_in_class=students_in_class, current_date=current_date.strftime('%d/%m/%y'), student_times=None, week=current_week(current_date), day=CONSTANT_DAYS[current_date.isoweekday()-1], prev_next=prev_next, viewing_day=day)
            
            
        # User is a teacher viewing the class of a student
        # For this one, show the attendance of the student and be able to change attendnance
        elif current_user.auth in ['teacher', 'admin'] and user.auth == 'student':
            form = AddStudentAttndTime(day=current_date.day, month=current_date.month)

            if request.method == "POST" and form.validate_on_submit():
                date = datetime.date(year=datetime.date.today().year, month=form.month.data, day=form.day.data)
                subject_datetime = check_class_date(date, subject)
                if subject_datetime:
                    duplicate_attendance_time = AttendanceTime.query.filter_by(time=datetime.datetime(year=date.year, month=date.month, day=date.day,
                                                                            hour=subject_datetime['subject'].time.start_time.hour,
                                                                            minute=subject_datetime['subject'].time.start_time.minute,
                                                                            second=subject_datetime['subject'].time.start_time.second),
                                                                            user=user.id, subject=subject.id).first()
                    if duplicate_attendance_time: # checks if there is already an attendance time for this subject and user on a particular day
                        # Updates the attendance status instead of adding a new entry to the database for this subject, user and time of attendance
                        if duplicate_attendance_time.attnd_status != form.status.data:
                            duplicate_attendance_time.attnd_status = form.status.data
                            try:
                                db.session.flush()
                            except:
                                db.session.rollback()
                                flash('Something went wrong, attendance status was not updated')
                            else:
                                db.session.commit()
                                flash('Successfully updated attendance for this date')
                        else:
                            flash('Attendance was not updated')
                    else:
                        # if there is no duplicate of the attendance time, user, and class then add a new entry for that attendance
                        # into the database
                        try:
                            new_time = AttendanceTime(time=datetime.datetime(year=date.year, month=date.month, day=date.day,
                                                      hour=subject_datetime['subject'].time.start_time.hour,
                                                      minute=subject_datetime['subject'].time.start_time.minute,
                                                      second=subject_datetime['subject'].time.start_time.second),
                                                      user=user.id, attnd_status=form.status.data, subject=subject.id)
                            db.session.add(new_time)
                            db.session.flush()
                        except:
                            db.session.rollback()
                        else:
                            db.session.commit()
                            flash('Successfully added new attendance to the database')
                else:
                    flash('Date was not a valid date for the subject')
            class_times = get_class_dates(subject) 
            user_attendance_times = AttendanceTime.query.filter_by(user=user.id, subject=subject.id).all()
            user_attendance_today = None
            for i in user_attendance_times:
                if i.time.date() == current_date:
                    user_attendance_today = i #BROKEN
            return render_template("teacherstudentclass.html", subject=subject, user=user, days=CONSTANT_DAYS, student_times=user_attendance_times, form=form, class_times=class_times,
                                   current_date=current_date.strftime('%d/%m/%y'), day=day, today_date=datetime.date.today().strftime('%d/%m/%y'), teacher=current_user, user_attendance_today=user_attendance_today)
        
        # User is a student and they're viewing their class
        elif (current_user.auth == 'student' and class_code in
            [x.subject.code for x in current_user.subjects]):
            # Gets the user's attendance times from the database
            student_attnd_times = AttendanceTime.query.filter_by(user=user.id, subject=subject.id).all()
            student_attnd_times_weeks = []
            for i in student_attnd_times:
                if ((ceil((i.time.timetuple().tm_yday)/7))) % 2 == 0:
                    student_attnd_times_weeks.append((i, i.time.timetuple().tm_wday, "A"))
                else:
                    student_attnd_times_weeks.append((i, i.time.timetuple().tm_wday, "B"))
            attendance_on_day = None
            for time in student_attnd_times:
                if time.time.date() == (datetime.date(2019, 12, 31) + datetime.timedelta(days=day)):
                    attendance_on_day = time
            return render_template("studentclass.html", subject=subject, days=CONSTANT_DAYS, attnd_times=student_attnd_times_weeks, attnd_day=attendance_on_day, current_date=current_date)
        
        # User is a student but they're not viewing one of their class
        else:
            flash('You do not have access to this page')
            return redirect(url_for('classes', user_code=current_user.user_code))
    return render_template("teacherclass.html", subject=subject)

# Account Route
@app.route('/account/<user_code>', methods=['GET', 'POST'])
@login_required
def account(user_code):
    # Checks if the user is a student and if they are viewing their own account page
    if current_user.auth == 'student':
        if current_user.user_code != user_code:
            # redirects the student if they're not viewing their own account page
            flash('You do not have access to this page')
            return redirect(url_for('home'))

    # This is only accesss able to users which are no students.
    # Queries the database for the user which is being viewed if there is no user
    # returned then the person viewing the page is redirected
    user = User.query.filter_by(user_code=user_code).first()
    if not user:
        flash('User does not exist')
        return redirect(url_for('home'))

    if current_user.auth == "admin" and user.auth != "admin":
        form = SetAuth(user_auth=user.auth)
        if request.method == 'POST' and form.validate_on_submit():
            user.auth = form.user_auth.data
            try:
                db.session.flush()
            except:
                db.session.rollback()
                flash("An Error Occured, failed to change user auth")
            else:
                db.session.commit()
                flash("Successfully changed user's auth")
    else:
        form = None
    return render_template("account.html", user=user, form=form)


# Route for logging attendance using a post reqeust from an external http client
@app.route('/logtime', methods=['POST'])
def logtime():
    try:
        user_code = request.form['user']
        card_uid = request.form['uid']
        scanner_id = request.form['scanner_id']
    except:
        print("Failed to obtain values")
        return "Error"
    else:
        user = User.query.filter_by(user_code=user_code).first()
        current_datetime = datetime.datetime.now()

        if not user:
            return "User not found"
        if card_uid not in [tag.tag_uid for tag in user.tags]:
            return "Unidentified Card"
        
        scanner = Scanner.query.filter_by(scanner_id=scanner_id).first()
        if not scanner:
            return "Unidentified Scanner"
        else:
            # Checks if the user is in the class/es which are associated with the scanner
            # if the user is in a class that is associated with the scanner, it will check current time with
            # the times of the scanner 
            # TODO: Leave it because its used for the RFID scanner
            # Broken because it doesnt check the day of week or week A/B of the time and it doesnt work if there are
            # two classes on the same scanner on that day
            for i in scanner.subject:
                for x in i.users:
                    if x.user == user:
                        for z in [y.time for y in i.times]:
                            if current_datetime.time() >= z.start_time and current_datetime.time() <= z.end_time:
                                try:
                                    new_time = AttendanceTime(time=current_datetime, user=user.id, attnd_status='present', subject=i.id)
                                    db.session.add(new_time)
                                    db.session.flush()
                                except:
                                    return 'An Error Occured'
                                else:
                                    return 'Success'
                        try:
                            new_time = AttendanceTime(time=current_datetime, user=user.id, attnd_status='N/A', subject=i.id)
                            db.session.add(new_time)
                            db.session.flush()
                        except:
                            return 'An Error Occured'
                        else:
                            return 'Success'
    return user_code



# TODO: create table for all the requested accounts to be scanned to card
@app.route("/get_users", methods=['GET'])
def get_users():
    
    return None

# Function for returning the start time, used for sorting times
def get_start_time(time):
    return time.start_time

# Route for setting default times which a subject/class can be on at
@app.route('/add_times', methods=['GET', 'POST'])
@login_required
def addtime():
    # Checking if the user is a teacher or not
    if current_user.auth not in ['teacher', 'admin']:
        flash('You do not have permission to access this page')
        return redirect(url_for('home'))
    
    form = AddTimesForm()
    if request.method == "POST" and form.validate_on_submit():
        # Turning the time taken from the form into a datetime in order to 
        # add one hour to it to get the ending time of the class
        dtime = datetime.datetime.combine(datetime.date(2000, 1, 1), form.time.data)
        # defining the end time of the class by adding one hour to the starting time
        end_time = dtime + datetime.timedelta(hours=1)

        # Adding the starting and ending times to the database
        time = Times(start_time=form.time.data, end_time=end_time.time())
        try:
            db.session.add(time)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            flash('The time entered in has already been added to the database')
        else:
            db.session.commit()
            flash('Time Successfully Added')
    # Getting all the times and presenting them in a chronological order
    times = sorted(Times.query.all(), key=get_start_time)
    return render_template('add_times.html', form=form, times=times)

# Route for deleting the possible times which a subject/class can be on at
@app.route('/delete_times', methods=['POST'])
@login_required
def removetime():
    if current_user.auth not in ['teacher', 'admin']:
        flash('You do not have permission to access this page')
        return redirect(url_for('addtime'))

    # Getting the id of the class to query the database for
    # and checking if the time which the user wants to delete is a
    # valid time
    try:
        time_id = int(request.form.get('time'))
    except ValueError:
        flash('Invalid value for time deletion')
    else:
        time = Times.query.filter_by(id=time_id).first()
        if time:
            # Deleting the entries with the time set as a FK
            for i in time.subjects:
                db.session.delete(i)
            # Deleting the time itself
            db.session.delete(time)
            db.session.commit()
            flash('Successfully deleted time')
        else:
            flash('Invalid time')
    return redirect(url_for('addtime'))

# Function for getting all the predefined times which a class could be set to
def get_times():
    times = sorted(Times.query.all(), key=get_start_time)
    return [(time.id, time.start_time) for time in times]
    
# Route for setting the time of a specific class/subject for each week and day
@app.route('/classes/<class_code>/settimes', methods=["GET", "POST"])
@login_required
def settimes(class_code):
    if current_user.auth not in ['teacher', 'admin']:
        flash('You do not have permission to access this page')
        return redirect(url_for('home'))

    # Checking if the class exists
    subject = SubjectCode.query.filter_by(code=class_code).first()
    if subject:
        set_times_form = SetTimesForm()
        # Getting the chocies/values for the selectfield called 'time' in the form for adding times to the subject
        set_times_form.time.choices = get_times()
        remove_times_form = UnsetTimesForm()
        # Getting the choices/values for the selectfield called 'time' in the form for removing times frpm the subject
        remove_times_form.time.choices = [(x.id, f"{x.time.start_time} {'Week A' if not x.sweek else 'Week B'} {CONSTANT_DAYS[x.sday]}") for x in subject.times]
        
        # validating and processing form the setting the times of a class
        if request.method == 'POST' and set_times_form.add.data and set_times_form.validate_on_submit():
            # Checking if the class already has a combination of day, time, and week
            if SubjectTimes.query.filter_by(subject_id=subject.id,
                                            stime_id=set_times_form.time.data,
                                            sweek=set_times_form.week.data,
                                            sday=set_times_form.day.data).first():
                flash('This time is already assocaited with the class')
            # Checking if the subject has the maxmium amount of times
            elif SubjectTimes.query.filter_by(subject_id=subject.id,
                                              sweek=set_times_form.week.data,
                                              sday=set_times_form.day.data).first():
                flash('This class already has a time on this day')
            elif len(subject.times) >= 10:
                flash('Maxmium amount of times of 10 for this classes reached.')
            # Setting the time for the class which the user entered into the form
            else:
                asso = SubjectTimes(sweek=set_times_form.week.data, sday=set_times_form.day.data)
                asso.time = Times.query.filter_by(id=set_times_form.time.data).first()
                subject.times.append(asso)
                db.session.commit()
                flash('Successfully set time')

        # Validating and processing form for removing the times of a class
        elif request.method == 'POST' and remove_times_form.remove.data and remove_times_form.validate_on_submit():
            try:
                remove_time = SubjectTimes.query.filter_by(id=remove_times_form.time.data).first()
                db.session.delete(remove_time)
                db.session.flush()
            except:
                db.session.rollback()
                flash('Unable to delete time')
            else:
                db.session.commit()
        
    else:
        flash('Class was not found')
        return redirect(url_for('classes', user_code=current_user.user_code))
    times = subject.times
    # Updating the select field for the remove_times_form
    form_choices = [(x.id, f"{x.time.start_time} {'Week A' if not x.sweek else 'Week B'} {CONSTANT_DAYS[x.sday]}") for x in subject.times]
    remove_times_form.time.choices = form_choices
    return render_template('settimes.html', form=set_times_form, remove_times_form=remove_times_form, times=times, days=CONSTANT_DAYS, form_choices=form_choices)

# Route for viewing all the students in the system
@app.route('/students', methods=['GET'])
@login_required
def students():
    if current_user.auth in ['teacher', 'admin']:
        students = User.query.filter_by(auth='student').all()
        my_students = []
        for subject in current_user.subjects:
            for user in subject.subject.users:
                if user.user.auth not in ['teacher', 'admin'] and user.user not in my_students:
                    my_students.append(user.user)
        return render_template('students.html', students=students, my_students=my_students)
    else:
        flash('You do not have access to this page')
        return redirect(url_for('home'))

# Route for adding a scanner to a subject/class
@app.route("/scanner", methods=['GET', 'POST'])
@login_required
def scanner():
    if current_user.auth not in ['teacher', 'admin']:
        flash('You do not have permission to access this page')
        return redirect(url_for('home'))
    
    add_scanner_form = AddScanner()
    # Defining the values/choices for the selectfield
    add_scanner_form.subject.choices = [(int(sub.id), sub.code) for sub in SubjectCode.query.all()]

    # Checking if the form is valind the request method was a POST
    if request.method == 'POST' and add_scanner_form.validate_on_submit():
        scan_id = add_scanner_form.scanner.data.strip().lower()
        # Checking if a particular subject already has a scanner associated to it. One subject can only have one scanner but one scanner can have multiple subjects
        if Scanner.query.filter_by(subject_id=add_scanner_form.subject.data).first():
            flash('Subject already has an associated scanner')
        else:
            # Adding the scanner and subject association to the database
            try:
                new_scanner = Scanner(scanner_id=scan_id, subject_id=add_scanner_form.subject.data)
                db.session.add(new_scanner)
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                flash('Subject was already associated with scanner')
            else:
                flash('Subject successfully added to scanner')
                db.session.commit()
    return render_template('scanner.html', form=add_scanner_form)

# Route for handling error 404
@app.errorhandler(404)
def error404(e):
    return render_template('error404.html')

# Route for handing error 405; Invlaid request method
@app.errorhandler(405)
def error405(e):
    flash('Invalid Request Method')
    return redirect(url_for('home'))

@app.errorhandler(500)
def error500(e):
    flash('An error occured on our side')
    return redirect(url_for('home'))

@app.route('/test', methods=['GET', 'POST'])
def test():
    print(current_user.tags)
    print([tag.tag_uid for tag in current_user.tags])
    return 'test'