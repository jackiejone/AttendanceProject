from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, IntegerField, PasswordField,
                     BooleanField, SubmitField, SelectMultipleField, )
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import Length, InputRequired, Email, EqualTo, ValidationError
from attendanceproject.models import *

def int_check(form, field):
    try:
        int(field.data)
    except ValueError:
        raise ValidationError('Student Code must be a whole number')

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
                                       Length(min=5, max=6, message='Student Code can only be 5 or 6 characters long'),
                                       int_check],
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
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message='Field Required'),
                                             Email(message='Invalid Email Address')],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(message='Field Required'),
                             Length(min=4)],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    
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
class JoinClassFields(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# Form for joining classes using boolean fields
class JoinClassForm(FlaskForm):
    classes = SubjectCode.query.all()
    sclasses = [(x.id, x.name) for x in classes]
    classesfield = JoinClassFields('Label', choices=sclasses)
    