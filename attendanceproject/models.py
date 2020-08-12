from attendanceproject import db, login_manager
from flask_login import UserMixin

# Database model

# Table for Users
class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    fname = db.Column(db.Text(20), nullable=False)
    lname = db.Column(db.Text(20), nullable=False)
    user_code = db.Column(db.Text(8), nullable=False, unique=True)
    email = db.Column(db.Text(50), nullable=False, unique=True)
    password = db.Column(db.Text(90), nullable=False)
    auth = db.Column(db.Text(10), nullable=True)
    tags = db.relationship('Tag', backref='user_tag')
    subjects = db.relationship('UserSubject', back_populates='user')
    attnd_times = db.relationship('AttendanceTime', backref='subject_attnd_times')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Table for associating signin times with the user
class AttendanceTime(db.Model):
    __tablename__ = "attnd_time"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    time = db.Column(db.DateTime, nullable=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attnd_status = db.Column(db.Text(10), nullable=False)
    subject = db.Column(db.Integer, db.ForeignKey('subject_code.id'), nullable=False)

class Scanner(db.Model):
    __tablename__ = "scanner"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    scanner_id = db.Column(db.Text(5), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject_code.id'), nullable=False, unique=True)
    subject = db.relationship("SubjectCode", back_populates="scanner")

# Table for storing RFID tags and associating them with a user (student) as one user could
# have multiple tags. The tags also have UIDs which can be used for authentication 
# (Students creating their own RFID tags)
class Tag(db.Model):
    __tablename__ = "user_tag"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    tag_uid = db.Column(db.Text(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Association table bewtween User and their subject/s (class/es)
class UserSubject(db.Model):
    __tablename__ = "user_subject"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Foreign Key
    user_type = db.Column(db.Text(10), nullable=False) # Teacher or student relationship to class
    subject_id = db.Column(db.Integer, db.ForeignKey('subject_code.id')) # Foreign Key
    user = db.relationship('User', back_populates='subjects')
    subject = db.relationship('SubjectCode', back_populates='users')

# Table for associating the time which a subject is on to the subject
class SubjectTimes(db.Model):
    __tablename__ = "subject_time"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject_code.id'))
    stime_id = db.Column(db.Integer, db.ForeignKey('times.id'), nullable=False)
    sweek = db.Column(db.Boolean, nullable=False)
    sday = db.Column(db.Integer, nullable=False)
    time = db.relationship('Times', back_populates='subjects')
    subject = db.relationship('SubjectCode', back_populates='times')

# Names and codes for each subject which a student could have
class SubjectCode(db.Model):
    __tablename__ = "subject_code"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.Text(50), nullable=False)
    code = db.Column(db.Text(50), unique=True, nullable=False)
    join_code = db.Column(db.Text(10), unique=True, nullable=False)
    users = db.relationship('UserSubject', back_populates='subject')
    times = db.relationship('SubjectTimes', back_populates='subject')
    scanner = db.relationship('Scanner', back_populates='subject')

# Table for storing the possible times for a class
class Times(db.Model):
    __tablename__ = "times"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    start_time = db.Column(db.Time, unique=True, nullable=False)
    end_time = db.Column(db.Time, unique=True, nullable=False)
    subjects = db.relationship("SubjectTimes", back_populates='time')

# Table for queueing data to be scanned onto tags
class TagQueue(db.Model):
    __tablename__ = "tag_queue"
    
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scanner = db.Column(db.Integer, db.ForeignKey('scanner.id'), nullable=False)
    