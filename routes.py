from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Defining database location
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "Attendance.db"))

# Defining and configuring app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SECRET_KEY'] = os.urandom(16)
db = SQLAlchemy(app)

from models import *
db.create_all() # Creates all tables

@app.route('/', methods=["GET"])
@app.route('/home', methods=["GET"])
def home():
    return render_template("home.html")

@app.route('/register')
def register():
    return 'register'

@app.route('/login')
def login():
    return 'login'

@app.route('/classes')
def classes():
    return 'classes'

@app.route('/classes/<class_code>')
def class_code(class_code):
    return class_code

@app.route('/account/<user>')
def account(user):
    return user

if __name__ == "__main__":
    app.run(debug=True)