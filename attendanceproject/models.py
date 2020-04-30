from attendanceproject import db, login_manager
from flask_login import UserMixin

# Database model

# Table for Users
class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    fname = db.Column(db.Text(20), nullable=False)
    lname = db.Column(db.Text(20), nullable=False)
    student_code = db.Column(db.Integer, nullable=False, unique=True)
    email = db.Column(db.Text(50), nullable=False, unique=True)
    password = db.Column(db.Text(80), nullable=False)
    auth = db.Column(db.Text(10), nullable=True)
    tags = db.relationship('Tag', backref='user_tag')
    subjects = db.relationship('UserSubject', back_populates='user')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    times = db.relationship('SubjectTimes', backref='subjects')

# Association table bewtween User and their subject/s (class/es)
class UserSubject(db.Model):
    __tablename__ = "user_subject"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign Key
    subject_id = db.Column(db.Integer, db.ForeignKey('subject_code.id'), nullable=False) # Foreign Key
    attnd_times = db.relationship('AttendanceTime', backref='subject_attnd_times')
    user = db.relationship('User', backref='user')
    subject = db.relationship('SubjectCode', backref='subject')

# Table for associating signin times with the user's class which their signing into
class AttendanceTime(db.Model):
    __tablename__ = "attnd_time"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    time = db.Column(db.Time, nullable=False) # Time field
    subject = db.Column(db.Integer, db.ForeignKey('user_subject.id'), nullable=False)

class SubjectTimes(db.Model):
    __tablename__ = "subject_times"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    subject = db.Column(db.Integer, db.ForeignKey('subject_code.id'), nullable=False)
    s_time = db.Column(db.Time, nullable=False)
    
    