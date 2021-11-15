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
from app_class import *
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
app.config['SECRET_KEY'] = 'Y6j^cPzk5b!&2&Hd'
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
    permission = db.Column(db.String(128), default='9000')
    profile_picture = db.Column(db.String(128), default='dd')
    guild = db.Column(db.String(128), default='')
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

def write_logs(line):
    data = Data.query.get(1)
    if data is None:
        data = Data()
        data.logs = line
        db.session.add(data)
        db.session.commit()
    else:
        logs = data.logs.splitlines()
        logs.append(line)
        while len(logs) > 500:
            del logs[0]
        data.logs = '\n'.join(logs)
        db.session.commit()

@app.route('/logs')
@login_required
def logs():
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    try:
        logs = Data.query.get(1).logs.splitlines()
    except:
        logs = ''
    return render_template('logs.html',
        logs=reversed(logs))

@app.route('/')
def index():
    try:
        bulletin = Data.query.get(1).bulletin
    except:
        bulletin = ''
    print(bulletin)
    return render_template('index.html',
        bulletin=bulletin)

@app.route('/update-bulletin', methods=['GET', 'POST'])
@login_required
def update_bulletin():
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    form = Bulletin()
    try:
        data = Data.query.get(1)
    except:
        flash("can't get data")
        return redirect(url_for('index'))
    print('-----------', data.bulletin)
    if request.method == 'POST':
        print('?')
        data.bulletin = request.form['text']
        print('-----------', data.bulletin)
        try:
            db.session.commit()
            flash('Bulletin Modifie')
            write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" updated bulletin")
            return redirect(url_for('index'))
        except:
            flash('Error During Update')
            return redirect(url_for('index'))
    return render_template('update-bulletin.html',
        form=form)

@app.route('/rules')
@login_required
def rules():
    return render_template('rules.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e): 
    return render_template('500.html'), 500

### USER ###
@app.route('/login', methods=['GET', 'POST'])
def login():
    login = None
    password = None
    user = None
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password_hash.data
        form.login.data = ''
        form.password_hash.data = ''
        user = Users.query.filter_by(login=login).first()
        if user is not None:
            if check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Mot de Passe Incorrect')
        else:
            flash("Cet Utilisateur n'existe pas")
    return render_template('login.html',
        login = login,
        form = form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Reviens vite UwU')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

def set_captcha():
    image = ImageCaptcha(width = 280, height = 60)
    random_string = ''
    for _ in range(random.randint(3, 4)):
        random_string += random.choice(string.ascii_lowercase)
    image.generate(random_string)  
    image.write(random_string, 'static/images/captcha.png')
    cache['captcha_str'] = random_string

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if not form.validate_on_submit() or cache['captcha_str'] is None:
        set_captcha()
    else:
        user = Users.query.filter_by(login=form.login.data).first()
        if user is None and form.captcha.data == cache['captcha_str']:
            hashed_pwd = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(login=form.login.data, 
                password_hash=hashed_pwd,
                date_added = datetime.now(pytz.timezone("Europe/Paris")))
            db.session.add(user)
            db.session.commit()
            cache['captcha_str'] = None
            form.login.data = ''
            form.password_hash.data = ''
            flash('User added')
            write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+user.login+" registered")
            return redirect(url_for('login'))
        if form.captcha.data != cache['captcha_str']:
            flash("Captcha Incorrect")
        if user is not None:
            flash("{} est deja utilise".format(user.login))
        set_captcha()
    return render_template('register.html',
        form = form)

@app.route('/users')
@login_required
def users():
    if current_user.permission < '1. Member':
        return render_template('403.html')
    users = None
    users = Users.query.order_by(Users.date_added.desc())
    return render_template('users.html',
        users = users)

@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = UserForm()
    user_update = Users.query.get_or_404(id)
    if current_user.permission < '2. Admin' or current_user.permission <= user_update.permission:
        return render_template('403.html')
    if request.method == 'POST':
        user_update.permission = request.form['permission']
        user_update.guild = request.form['guild']
        try:
            db.session.commit()
            flash('Utilisateur Modifie')
            write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" updated "+user_update.login)
            return redirect(url_for('users'))
        except:
            flash('Error During Update')
            return redirect(url_for('users'))
    return render_template('update-user.html',
        form = form,
        user_update = user_update)

@app.route('/update-password/<int:id>', methods=['GET', 'POST'])
@login_required
def update_password(id):
    form = UserForm()
    password_update = Users.query.get_or_404(id)
    if current_user.id is not id or current_user.permission < '1. Member':
        return render_template('403.html')
    if request.method == 'POST':
        if request.form['password_hash'] == request.form['password_hash_confirm']:
            hashed_pwd = generate_password_hash(request.form['password_hash'], "sha256")
            password_update.password_hash = hashed_pwd
            try:
                db.session.commit()
                flash('Mot de Passe Modifie')
                return redirect(url_for('dashboard'))
            except:
                flash('Error During Update')
                return redirect(url_for('dashboard'))
        flash("Les Mots de Passe doivent correspondre")
    return render_template('update-password.html',
        form = form,
        password_update = password_update)

@app.route('/update-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def update_profile(id):
    form = UserForm()
    profile_update = Users.query.get_or_404(id)
    if current_user.id is not id or current_user.permission < '1. Member':
        return render_template('403.html')
    if request.method == 'POST':
        user = Users.query.filter_by(login=form.login.data).first()
        if re.match(re.compile(r"^(?=.{4,20}$)[a-zA-Z0-9-]*$"), request.form['login']):
            if user is None or current_user.login == request.form['login']:
                profile_update.login = request.form['login']
                profile_update.profile_picture = request.form['profile_picture']
                profile_update.guild = request.form['guild']
                try:
                    db.session.commit()
                    flash('Profil Modifie')
                    return redirect(url_for('dashboard'))
                except:
                    flash('Error During Update')
                    return redirect(url_for('dashboard'))
        else:
            flash("Login doit etre alphanum et 4 a 20 char")
        if user is not None:
            flash("{} est deja utilise".format(user.login))
    return render_template('update-profile.html',
        form = form,
        profile_update = profile_update)

@app.route('/delete-user/<int:id>/<prev_link>')
@login_required
def delete_user(id, prev_link):
    user_delete = Users.query.get_or_404(id)
    if current_user.permission < '2. Admin' or current_user.permission <= user_delete.permission:
        return render_template('403.html')
    try:
        db.session.delete(user_delete)
        db.session.commit()
        flash('Utilisateur {} supprime'.format(user_delete.login))
        write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" deleted user "+user_delete.login)
        user_delete.login = ''
        user_delete.permission = ''
        return redirect(url_for(prev_link))
    except:
        flash('Error During Delete')
        return redirect(url_for(prev_link))

@app.route('/confirm-delete/<item>/<int:id>/<prev_link>')
@login_required
def confirm_delete(item, id, prev_link):
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    return render_template('confirm-delete.html',
        item=item,
        id=id,
        prev_link=prev_link)

### MATCH ###
@app.context_processor
def global_var():
    matchs = MatchPost.query.order_by(MatchPost.date_posted.desc())
    users = Users.query.order_by(Users.login)
    matchs_to_valid = 0
    users_to_valid = 0
    for match in matchs:
        if not match.valid:
            matchs_to_valid += 1
    for user in users:
        if user.permission == '':
            users_to_valid += 1
    return dict(matchs_to_valid=matchs_to_valid,
                users_to_valid=users_to_valid)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/valid-match/<int:id>')
@login_required
def valid_match(id):
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    valid_match = MatchPost.query.get_or_404(id)
    valid_match.valid = 1
    try:
        db.session.commit()
        flash('Match Valide')
        write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" validated match "+str(valid_match.id))
        return redirect(url_for('matchs_to_valid'))
    except:
        flash('Error')
        return redirect(url_for('matchs_to_valid'))

@app.route('/remove-match/<int:id>')
@login_required
def remove_match(id):
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    valid_match = MatchPost.query.get_or_404(id)
    valid_match.valid = 0
    try:
        db.session.commit()
        flash('Match Retire')
        write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" removed match "+str(valid_match.id))
        return redirect(url_for('matchs'))
    except:
        flash('Error')
        return redirect(url_for('matchs'))

@app.route('/matchs-to-valid')
@login_required
def matchs_to_valid():
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    match_list = []
    matchs = MatchPost.query.order_by(MatchPost.date_posted.desc())
    for match in matchs:
        new_match = Match()
        new_match.id = match.id
        new_match.type = match.type
        new_match.objective = match.objective
        new_match.allies_login = match.allies_login
        new_match.nb_allies = match.nb_allies
        new_match.nb_enemies = match.nb_enemies
        new_match.code = match.code
        new_match.author = match.author
        new_match.date_posted = match.date_posted
        nb_enemies = int(match.nb_enemies)
        if match.objective == "prisme":
            nb_enemies += 5
        for code in match.code.split():
            nb_enemies += int(code)
        if match.type == "def":
            nb_enemies += 2
        new_match.points = round(10 * int(nb_enemies) / int(match.nb_allies))
        new_match.valid = match.valid
        match_list.append(new_match)
    return render_template('matchs-to-valid.html',
        match_list=match_list)  

@app.route('/matchs')
@login_required
def matchs():
    match_list = []
    matchs = MatchPost.query.order_by(MatchPost.date_posted.desc())
    for match in matchs:
        new_match = Match()
        new_match.id = match.id
        new_match.type = match.type
        new_match.objective = match.objective
        new_match.allies_login = match.allies_login
        new_match.nb_allies = match.nb_allies
        new_match.nb_enemies = match.nb_enemies
        new_match.code = match.code
        new_match.author = match.author
        new_match.date_posted = match.date_posted
        nb_enemies = int(match.nb_enemies)
        if match.objective == "prisme":
            nb_enemies += 5
        for code in match.code.split():
            nb_enemies += int(code)
        if match.type == "def":
            nb_enemies += 2
        new_match.points = round(10 * int(nb_enemies) / int(match.nb_allies))
        new_match.valid = match.valid
        match_list.append(new_match)
    return render_template('matchs.html',
        match_list=match_list)

@app.route('/delete-match/<int:id>/<prev_link>')
@login_required
def delete_match(id, prev_link):
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    match_delete = MatchPost.query.get_or_404(id)
    try:
        db.session.delete(match_delete)
        db.session.commit()
        flash('Match {} supprime'.format(match_delete.id))
        write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" deleted match "+str(match_delete.id))
        return redirect(url_for(prev_link))
    except:
        return redirect(url_for(prev_link))

@app.route('/static/screen/<int:id>')
@login_required
def get_img(id):
    img = MatchPost.query.get_or_404(id)
    return Response(img.screen, mimetype=img.mimetype)

@app.route('/post-match', methods=['GET', 'POST'])
@login_required
def post_match():
    if current_user.permission < '1. Member':
        return render_template('403.html')
    users = Users.query.order_by(Users.login)
    form = MatchForm()
    user_list = []
    allies_login = ""
    for user in users:
        user_list.append((str(user.id), user.login))
    form.allies_list.choices = user_list
    if request.method == 'POST':
        if not allowed_file(form.screen.data.filename):
            flash('Fichier non supporte')
            return render_template('post-match.html',
                users=users,
                form=form)
        filename = form.screen.data.read()
        for id in form.allies_selected.data:
            allie = Users.query.get_or_404(id)
            allies_login += allie.login+" "
        match = MatchPost(type=form.type.data,
            objective=form.objective.data,
            allies_id=" ".join(form.allies_selected.data),
            allies_login=allies_login,
            nb_allies=form.nb_allies.data,
            nb_enemies=form.nb_enemies.data,
            code=" ".join(form.code.data),
            screen=filename,
            mimetype=form.screen.data.mimetype,
            author=current_user.login,
            date_posted=datetime.now(pytz.timezone("Europe/Paris")))
        form.type.data = ''
        form.objective.data = ''
        form.allies_list.data = ''
        form.allies_selected.data = ''
        form.nb_allies.data = ''
        form.nb_enemies.data = ''
        form.code.data = ''
        form.screen.data = ''
        db.session.add(match)
        db.session.commit()
        flash('Match Poste')
        write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" posted match "+str(match.id))
    return render_template('post-match.html',
        users=users,
        form=form) 

@app.route('/update-match/<int:id>', methods=['GET', 'POST'])
@login_required
def update_match(id):
    if current_user.permission < '2. Admin':
        return render_template('403.html')
    form = MatchForm()
    match_update = MatchPost.query.get_or_404(id)
    users = Users.query.order_by(Users.login)
    user_list = []
    allies_login = ""
    for user in users:
        user_list.append((str(user.id), user.login))
    form.allies_list.choices = user_list
    for id in match_update.allies_id.split():
        allie = Users.query.get_or_404(id)
        form.allies_selected.choices.append((str(allie.id), allie.login))
    if request.method == 'POST':
        for id in form.allies_selected.data:
            allie = Users.query.get_or_404(id)
            allies_login += allie.login+" "
        match_update.type = form.type.data
        match_update.objective = form.objective.data
        match_update.allies_id = " ".join(form.allies_selected.data)
        match_update.allies_login = allies_login
        match_update.nb_allies = form.nb_allies.data
        match_update.nb_enemies = form.nb_enemies.data
        match_update.code = " ".join(form.code.data)
        try:
            db.session.commit()
            flash('Match Modifie')
            write_logs(str(datetime.now(pytz.timezone("Europe/Paris")))+' | '+current_user.login+" updated match "+str(match_update.id))
            return redirect(url_for('matchs_to_valid'))
        except:
            flash('Error During Update')
            return redirect(url_for('matchs_to_valid'))
    return render_template('update-match.html',
        form=form,
        match_update=match_update)

### LADDER ###
@app.route('/ladder/<int:month>-<int:year>/<guild>', methods=['GET', 'POST'])
@login_required
def ladder(month, year, guild):
    season_list = []
    ladder_list = []
    guild_list = []
    users = Users.query.order_by(Users.login)
    matchs = MatchPost.query.order_by(MatchPost.date_posted.desc())
    for user in users:
        if user.guild not in guild_list:
            guild_list.append(user.guild)
        if guild == '0' or user.guild == guild:
            allie = Ladder()
            allie.id = user.id
            allie.login = user.login
            allie.guild = user.guild
            allie.profile_picture = user.profile_picture
            ladder_list.append(allie)
    for match in matchs:
        if match.valid:
            if (match.date_posted.month, match.date_posted.year) not in season_list:
                    season_list.append((match.date_posted.month, match.date_posted.year))
            if month == 0 or (match.date_posted.month == month and match.date_posted.year == year):
                for id in  match.allies_id.split():
                    try :
                        allie = next(allie for allie in ladder_list if allie.id == int(id))
                        nb_enemies = int(match.nb_enemies)
                        if match.objective == "prisme":
                            nb_enemies += 5
                        for code in match.code.split():
                            nb_enemies += int(code)
                        if match.type == "atk":
                            allie.nb_atk += 1
                            allie.pt_atk += round(10 * int(nb_enemies) / int(match.nb_allies))
                        if match.type == "def":
                            nb_enemies += 2
                            allie.nb_def += 1
                            allie.pt_def += round(10 * int(nb_enemies) / int(match.nb_allies))
                        allie.pt_total = allie.pt_atk + allie.pt_def
                        allie.nb_total = allie.nb_atk + allie.nb_def
                    except:
                        pass
    return render_template('ladder.html',
        ladder_list=sorted(ladder_list, key=lambda x: x.pt_total, reverse=True),
        month=month,
        year=year,
        guild=guild,
        season_list=season_list,
        guild_list=guild_list)

### MAIN ###
if __name__=='__main__': 
    app.run(debug=False)