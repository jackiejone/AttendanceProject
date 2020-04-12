from flask_sqlalchemy import SQLAlchemy
from routes import db

# Database model

class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    fname = db.Column(db.Text(20), nullable=False)
    lname = db.Column(db.Text(20), nullable=False)
    student_code = db.Column(db.Integer, nullable=False, unique=True)
    
class UserTag(db.model):
    __tablename__ = "user_tag"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    student_code = db.Column(db.Integer, nullable=False) # Foreign Key
    tag_uid = db.Column(db.Text(50), nullable=False, unique=True)
    
class SubjectCode(db.model):
    __tablename__ = "subject_code"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    code = db.Column(db.Text(50), unique=True, nullable=False)
    
class UserSubject(db.Model):
    __tablename__ = "user_subject"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # Foreign Key
    subject_id = db.Column(db.Integer, nullable=False) # Foreign Key
    
class AttendanceTime(db.Model):
    __tablename__ = "attnd_time"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    subject = db.Column(db.Interger, nullable=False ) # Foreign Key
    time = db.Column(db.Time, nullable=False) # Time