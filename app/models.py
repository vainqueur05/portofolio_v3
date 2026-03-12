# app/models.py

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --- Modèle utilisateur (admin) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# --- Modèle Projet ---
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description_courte = db.Column(db.String(300), nullable=False)
    description_longue = db.Column(db.Text, nullable=True)
    image_principale = db.Column(db.String(200), nullable=False, default='default.jpg')
    # Pour gérer plusieurs images, on pourrait créer une table séparée, mais on simplifie pour l'instant
    # On stocke les noms des images secondaires sous forme de chaîne séparée par des virgules
    images_secondaires = db.Column(db.Text, nullable=True)  # ex: "img1.jpg,img2.jpg"
    technologies = db.Column(db.Text, nullable=True)  # stockées sous forme de liste séparée par des virgules
    lien_demo = db.Column(db.String(300), nullable=True)
    lien_code = db.Column(db.String(300), nullable=True)
    date = db.Column(db.String(20), nullable=True)
    client = db.Column(db.String(100), nullable=True)
    categorie = db.Column(db.String(100), nullable=True)

    def get_technologies_list(self):
        if self.technologies:
            return [t.strip() for t in self.technologies.split(',')]
        return []

    def set_technologies_list(self, tech_list):
        self.technologies = ','.join(tech_list)

    def get_images_secondaires_list(self):
        if self.images_secondaires:
            return [img.strip() for img in self.images_secondaires.split(',') if img.strip()]
        return []

    def set_images_secondaires_list(self, img_list):
        self.images_secondaires = ','.join(img_list)

    def __repr__(self):
        return f'<Project {self.titre}>'

# --- Modèle Service ---
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icone = db.Column(db.String(50), nullable=False, default='bi-briefcase')
    prix = db.Column(db.String(50), nullable=True)
    # Les fonctionnalités : stockées sous forme de texte avec un séparateur (par exemple une par ligne)
    features = db.Column(db.Text, nullable=True)

    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split('\n') if f.strip()]
        return []

    def set_features_list(self, features_list):
        self.features = '\n'.join(features_list)

    def __repr__(self):
        return f'<Service {self.titre}>'

# --- Modèle Témoignage ---
class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auteur = db.Column(db.String(100), nullable=False)
    fonction = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200), nullable=True, default='default-avatar.jpg')
    message = db.Column(db.Text, nullable=False)
    note = db.Column(db.Integer, nullable=True)  # note sur 5
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Testimonial {self.auteur}>'

# --- Modèle Bio (informations de la page "À propos") ---
# On utilise un singleton : une seule ligne dans la table
class Bio(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=1)  # seul enregistrement avec id=1
    nom = db.Column(db.String(100), nullable=False, default='Ton Nom')
    titre = db.Column(db.String(200), nullable=False, default='Développeur Web')
    bio_paragraphes = db.Column(db.Text, nullable=True)  # stockés avec séparateur
    localisation = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    disponible = db.Column(db.Boolean, default=True)
    # Compétences sous forme de JSON ou texte structuré ? On peut stocker en JSON
    competences = db.Column(db.JSON, nullable=True)  # exemple: {"langages":["Python","JS"], "frameworks":["Flask"]}
    avatar = db.Column(db.String(200), nullable=True, default='avatar.jpg')

    def get_bio_paragraphes_list(self):
        if self.bio_paragraphes:
            return [p.strip() for p in self.bio_paragraphes.split('\n') if p.strip()]
        return []

    def set_bio_paragraphes_list(self, paragraphs):
        self.bio_paragraphes = '\n'.join(paragraphs)

    @classmethod
    def get_singleton(cls):
        bio = cls.query.get(1)
        if not bio:
            bio = cls(id=1)
            db.session.add(bio)
            db.session.commit()
        return bio