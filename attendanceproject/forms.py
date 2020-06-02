from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, IntegerField, PasswordField,
                     BooleanField, SubmitField, SelectMultipleField, FieldList, FormField)
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import Length, InputRequired, Email, EqualTo, ValidationError, AnyOf
from attendanceproject.models import *
from flask_login import current_user


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
                                           class_check, class_num_check], render_kw={'placeholder': '6 Letters'})
    join = SubmitField('Join Class')