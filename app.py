from flask import Flask, render_template, flash, request, redirect, url_for, Response, session as cache
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
from captcha.image import ImageCaptcha
import random
import string
import re
import os
import sys

### CMD ###
'''
python -m venv virt;
source virt/Scripts/activate;
export FLASK_ENV=development;
export FLASK_APP=app.py;
deactivate

flask run
flask db init
flask db migrate
flask db upgrade

winpty python
from app import db
db.create_all()

export FLASK_ENV=development ;
export FLASK_APP=app.py ;
python -m flask run
'''

### CONFIG ###
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
uri = os.environ.get("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SECRET_KEY'] = 'Y6j^cPzk5b!&2&Td'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 2
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

### USER DB ###
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    permission = db.Column(db.String(128), default='')
    profile_picture = db.Column(db.String(128), default='dd')
    date_added = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Paris")))

    @property
    def password(self):
        raise AttributeError('Password Unreadable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repre__(self):
        return '<login %r>' % self.login

### MATCH DB ###
class MatchPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128))
    objective = db.Column(db.String(128))
    allies_id = db.Column(db.String(128))
    allies_login = db.Column(db.String(128))
    nb_allies = db.Column(db.String(128))
    nb_enemies = db.Column(db.String(128))
    code = db.Column(db.String(128), default=0)
    screen = db.Column(db.LargeBinary)
    mimetype = db.Column(db.String(256))
    author = db.Column(db.String(128))
    date_posted = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Paris")))
    valid = db.Column(db.Boolean, default=0)

### DATA DB ###
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logs = db.Column(db.Text)
    bulletin = db.Column(db.String(256))

### APP ###
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html',
        bulletin="")