import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.secret_key = os.urandom(24)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/maria/Desktop/New_folder/TTMS/ttms/instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()
bcrypt = Bcrypt()

db.init_app(app)
bcrypt.init_app(app)

from ttms import routes

