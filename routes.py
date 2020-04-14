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

if __name__ == "__main__":
    app.run(debug=True)