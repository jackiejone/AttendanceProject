from flask_sqlalchemy import SQLAlchemy
from routes import db

# Database model

# Table for Users
class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    fname = db.Column(db.Text(20), nullable=False)
    lname = db.Column(db.Text(20), nullable=False)
    student_code = db.Column(db.Integer, nullable=False, unique=True)
    auth = db.Column(db.Text(10), nullable=True)
    tags = db.relationship('UserTag', backref='user_tag')
    subjects = db.relationship('UserSubject', back_populates='user')

# Table for storing RFID tags and associating them with a user (student) as one user could
# have multiple tags. The tags also have UIDs which can be used for authentication 
# (Students creating their own RFID tags)
class Tag(db.Model):
    __tablename__ = "user_tag"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    tag_uid = db.Column(db.Text(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Names and codes for each subject which a student could have
class SubjectCode(db.Model):
    __tablename__ = "subject_code"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.Text(50), nullable=False)
    code = db.Column(db.Text(50), unique=True, nullable=False)
    join_code = db.Column(db.Text(10), unique=True, nullable=False)
    users = db.relationship('UserSubject', back_populates='subject')
    times = db.relationship('SubjectTimes', backref='subject')

# Association table bewtween User and their subject/s (class/es)
class UserSubject(db.Model):
    __tablename__ = "user_subject"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign Key
    subject_id = db.Column(db.Integer, db.ForeignKey('subject_code.id'), nullable=False) # Foreign Key
    attnd_times = db.relationship('AttendanceTime', backref='subject')
    user = db.relationship('User', back_populates='user')
    subject = db.relationship('SubjectCode', back_populates='subject')

# Table for associating signin times with the user's class which their signing into
class AttendanceTime(db.Model):
    __tablename__ = "attnd_time"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    time = db.Column(db.Time, nullable=False) # Time field
    subject = db.Column(db.Integer, db.ForeignKey('user_subject.id'), nullable=False)

class SubjectTimes(db.model):
    __tablename__ = "subject_times"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    subject = db.Column(db.Integer, db.ForeignKey('subject_code.id'), nullable=False)
    s_time = db.Column(db.Time, nullable=False)
    
    