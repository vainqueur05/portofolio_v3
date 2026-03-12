# app/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Optional, URL, Length

class LoginForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired()])
    password = StringField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class ProjectForm(FlaskForm):
    titre = StringField('Titre', validators=[DataRequired(), Length(max=200)])
    description_courte = TextAreaField('Description courte', validators=[DataRequired(), Length(max=300)])
    description_longue = TextAreaField('Description longue', validators=[Optional()])
    image_principale = FileField('Image principale', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'])])
    images_secondaires = FileField('Images secondaires (sélectionnez plusieurs)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'])], render_kw={'multiple': True})
    technologies = StringField('Technologies (séparées par des virgules)', validators=[Optional()])
    lien_demo = StringField('Lien de démo', validators=[Optional(), URL()])
    lien_code = StringField('Lien du code source', validators=[Optional(), URL()])
    date = StringField('Date (ex: 2025)', validators=[Optional()])
    client = StringField('Client', validators=[Optional()])
    categorie = StringField('Catégorie', validators=[Optional()])
    submit = SubmitField('Enregistrer')

class ServiceForm(FlaskForm):
    titre = StringField('Titre', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    icone = StringField('Icône Bootstrap (ex: bi-briefcase)', validators=[Optional()], default='bi-briefcase')
    prix = StringField('Prix indicatif', validators=[Optional()])
    features = TextAreaField('Fonctionnalités (une par ligne)', validators=[Optional()])
    submit = SubmitField('Enregistrer')

class TestimonialForm(FlaskForm):
    auteur = StringField('Nom du client', validators=[DataRequired(), Length(max=100)])
    fonction = StringField('Fonction / Entreprise', validators=[Optional(), Length(max=100)])
    avatar = FileField('Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'])])
    message = TextAreaField('Témoignage', validators=[DataRequired()])
    note = IntegerField('Note (1-5)', validators=[Optional()])
    submit = SubmitField('Enregistrer')

class BioForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    titre = StringField('Titre professionnel', validators=[DataRequired(), Length(max=200)])
    bio_paragraphes = TextAreaField('Biographie (chaque paragraphe sur une nouvelle ligne)', validators=[Optional()])
    localisation = StringField('Localisation', validators=[Optional(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    disponible = BooleanField('Disponible pour des missions')
    competences_langages = StringField('Langages (séparés par des virgules)', validators=[Optional()])
    competences_frameworks = StringField('Frameworks (séparés par des virgules)', validators=[Optional()])
    competences_outils = StringField('Outils (séparés par des virgules)', validators=[Optional()])
    avatar = FileField('Photo de profil', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'webp'])])
    submit = SubmitField('Enregistrer')