from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, IntegerField, PasswordField,
                     BooleanField, SubmitField, SelectMultipleField, FieldList,
                     FormField, RadioField, DateField)
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import Length, InputRequired, Email, EqualTo, ValidationError, AnyOf, StopValidation
from wtforms.fields.html5 import TimeField
from attendanceproject.models import *
from flask_login import current_user
import datetime


# form for registering to the application
class RegisterForm(FlaskForm):
    fname = StringField('First Name',
                        validators=[Length(min=1, max=20),
                                    InputRequired(message='Input Requried')],
                        render_kw={"placeholder": "First Name"})
    lname = StringField('Last Name',
                        validators=[Length(min=1, max=20),
                                    InputRequired(message='Input Requried')],
                        render_kw={"placeholder": "Last Name"})
    std_code = StringField('Student Code',
                           validators=[InputRequired(message='Field Required'),
                                       Length(min=5, max=6,
                                              message='Student Code can only be 5 or 6 characters long')],
                           render_kw={"placeholder": "Student Code"})
    email = StringField('Email', validators=[InputRequired(message='Field Required'),
                                             Email(message='Invalid Email Address')],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(message='Field Required'),
                             Length(min=4)],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(message='Field Required'),
                             Length(min=4), EqualTo('password', message='Passwords Did not match')],
                                    render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')

# Form for logging into the application
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message='Field Required'),
                                             Email(message='Invalid Email Address')],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(message='Field Required'),
                             Length(min=4)],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    
# Form for creating a new class/subject
class CreateClassForm(FlaskForm):
    cname = StringField('Class Name', validators=[InputRequired(message='Fied Required'),
                                                  Length(max=50)],
                        render_kw={"placeholder": "Class Name"})
    ccode = StringField('Class Code', validators=[InputRequired(message='Fied Required'),
                                                  Length(max=50)],
                        render_kw={"placeholder": "Class Code"})
    auto_add = BooleanField('Join Class')
    submit = SubmitField('Create Class')


# Dynamic boolean fields for each class
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# Custom validator for checking if the amount of classes the user
# is trying to join is more than 6, the maxmium amount.
def my_length_check(form, field):
    if len(field.data) > 6 :
        raise ValidationError('Maxmium number of classes which can be selected is 6')
    
# Custom validator for checking if the user has already joined the maxmimum
# amount of classes allowed to join
def class_num_check(form, field):
    user_subjects = current_user.subjects
    if len(user_subjects) >= 6:
        raise ValidationError('Maxmium of 6 classes reached')
 
# Form for joining classes using boolean fields
class JoinClassForm(FlaskForm):
    classes = MultiCheckboxField('Classes', coerce=int, validators=[my_length_check])
    submit = SubmitField('Join Classes')

# Custom validator for checking if the code for a class exists
def class_check(form, field):
    if not SubjectCode.query.filter_by(join_code=field.data).first():
        raise ValidationError('Invalid Class Code')

# Form for joining a class through the unique class code
class CodeJoinForm(FlaskForm):
    code = StringField('Code', validators=[InputRequired(),
                                           Length(min=6, max=6, message='Field must be 6 characters long'),
                                           class_check, class_num_check], render_kw={'placeholder': '6 Characters'})
    join = SubmitField('Join Class')


# Validator for checking if the times in the form are within range or already in the database
def check_time(form, field):
        if field.data > datetime.time(hour=13, minute=50) or field.data < datetime.time(hour=8, minute=15):
            raise ValidationError(message="Minium Time is 8.15am and Maxium Time is 1.50pm")
        if Times.query.filter_by(start_time=field.data).first():
            raise ValidationError(message="Time Already Taken")

# Form for adding times to the database
class AddTimesForm(FlaskForm):
    time = TimeField(label='Add a Time', format='%H:%M', validators=[check_time, InputRequired()])
    add_time = SubmitField('Confirm')

# Form for associating a time with a class/subject
class SetTimesForm(FlaskForm):
    time = SelectField('Start Time', validators=None, coerce=int)
    week = RadioField('Week', choices=[(0, 'A'), (1, 'B')], coerce=int)
    day = SelectField('Day', choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
                                      (3, 'Thursday'), (4, 'Friday')], coerce=int)
    add = SubmitField('Add Time')

# Form for dissociating a time with a class/subject
class UnsetTimesForm(FlaskForm):
    time = SelectField('Time', coerce=int)
    remove = SubmitField('Remove Time')

# Form for associating a scanner with a class
class AddScanner(FlaskForm):
    scanner = StringField('Scanner ID', validators=[InputRequired(),
                                           Length(min=1, max=5, message='Scanner ID has a max 5 Characters')], render_kw={'placeholder': 'Scanner ID'})
    subject = SelectField('Subject', coerce=int)
    submit = SubmitField('Submit')

class AddStudentAttndTime(FlaskForm):
    day = SelectField("Day", choices=[(x , x) for x in range(1, 32)], coerce=int)
    month = SelectField("Month", choices=[(x, x) for x in range(1, 13)], coerce=int)
    status = SelectField('Attendance Status', choices=[('present', 'Present'), ('late', 'Late'), ('absent', 'Absent')], coerce=str, validators=[InputRequired()])
    submit = SubmitField('Submit')

class SetAuth(FlaskForm):
    user_auth = SelectField("Authentication", choices=[("teacher", "Teacher"), ("student", "Student")])
    submit = SubmitField('Change')