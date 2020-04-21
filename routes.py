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
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/classes')
def classes():
    return render_template("my_classes.html")

@app.route('/classes/<class_code>')
def class_code(class_code):
    return render_template("class.html")

@app.route('/account/<user>')
def account(user):
    return render_template("account.html")

if __name__ == "__main__":
    app.run(debug=True)