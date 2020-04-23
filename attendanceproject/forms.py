from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, InputRequired, Email, EqualTo

class RegisterForm(FlaskForm):
    fname = StringField('First Name',
                        validators=[Length(min=1, max=20),
                                    InputRequired(message='Input Requried')])
    lname = StringField('Last Name',
                        validators=[Length(min=1, max=20),
                                    InputRequired(message='Input Requried')])
    std_code = StringField('Student Code',
                           validators=[InputRequired(message='Input Required'),
                                       Length(min=5, max=6)])
    email = StringField('Email', validators=[InputRequired(message='Input Required'),
                                             Email(message='Invalid Email Address')])
    password = PasswordField('Password', validators=[InputRequired(message='Input Required'),
                             Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(message='Input Required'),
                             Length(min=4), EqualTo('password', message='Passwords Did not match')])
    submit = SubmitField('Register')
    