from flask_wtf import FlaskForm
from werkzeug.datastructures import MultiDict
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectMultipleField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, EqualTo, Regexp
from wtforms.widgets import TextArea

### USER ###
class UserForm(FlaskForm):
    login = StringField('Pseudo', validators=[DataRequired(), Regexp('^(?=.{4,12}$)[a-zA-Z0-9]*$', message="Login must be alphanum and 4-12 long")])
    password_hash = PasswordField('Mot de Passe', validators=[DataRequired()])
    password_hash_confirm = PasswordField('Confirmation Mot de Passe', validators=[DataRequired(), EqualTo('password_hash', message="Passwords must match")])
    captcha = StringField('Captcha', validators=[DataRequired()])
    permission = StringField('Permission')
    profile_picture = StringField('Photo de Profil')
    submit = SubmitField('Valider')

class LoginForm(FlaskForm):
    login = StringField('Pseudo', validators=[DataRequired()])
    password_hash = PasswordField('Mot de Passe', validators=[DataRequired()])
    submit = SubmitField('Valider')

### MATCH ###
class MatchForm(FlaskForm):
    type = StringField('Type', validators=[DataRequired()])
    allies_selected = SelectMultipleField('allies_selected', choices=[], validators=[DataRequired()])
    allies_list = SelectMultipleField('Allies', choices=[])
    objective = StringField('Objectif', validators=[DataRequired()])
    nb_allies = StringField('Nombre Allies', validators=[DataRequired()])
    nb_enemies = StringField('Nombre Ennemis', validators=[DataRequired()])
    code = SelectMultipleField('Code', choices=[(0, "Audio no noob no arnak (+0)"),
                                                (3, "River (+3)"),
                                                (2, "Def de Nuit 1h-8h (+2)")])
    screen = FileField('Screen', validators=[DataRequired()])
    submit = SubmitField('Valider')

class Match():
    id = 0
    type = ''
    objective = ''
    allies_login = ''
    nb_allies = ''
    nb_enemies = ''
    code = ''
    author = ''
    date_posted = ''
    points = ''
    valid = 0

### LADDER ###
class Ladder():
    id = 0
    login = ''
    profile_picture = ''
    pt_atk = 0
    pt_def = 0
    pt_total = 0
    nb_atk = 0
    nb_def = 0
    nb_total = 0

### BULLETIN ###
class Bulletin(FlaskForm):
    text = StringField('Text', widget=TextArea())
    submit = SubmitField('Valider')