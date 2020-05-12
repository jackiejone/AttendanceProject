from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, InputRequired, Email, EqualTo, ValidationError

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
    submit = SubmitField('Create Class')