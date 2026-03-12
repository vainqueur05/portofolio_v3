# app/admin/routes.py

import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Project
from app.forms import LoginForm, ProjectForm
from app.admin import bp
from app.models import Project, Service, Testimonial  # en haut du fichier
from app.forms import LoginForm, ProjectForm, ServiceForm, TestimonialForm, BioForm


@bp.route('/logs')
@login_required
def view_logs():
    log_file = current_app.config['LOG_FILE']
    lines = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()[-100:]  # dernières 100 lignes
        except Exception as e:
            lines = [f"Erreur de lecture du fichier de logs : {e}"]
    return render_template('admin/logs.html', logs=lines)

@bp.route('/dashboard')
@login_required
def admin_dashboard():
    project_count = Project.query.count()
    service_count = Service.query.count()
    testimonial_count = Testimonial.query.count()
    return render_template('admin/dashboard.html',
                           project_count=project_count,
                           service_count=service_count,
                           testimonial_count=testimonial_count)

# --- Fonctions utilitaires pour les uploads ---
from werkzeug.utils import secure_filename
import os

def save_file(file, subfolder='projects'):
    """Sauvegarde un fichier uploadé et retourne son nom"""
    if file is None:
        return None
    # Vérifier que l'objet a l'attribut filename (c'est un FileStorage)
    if not hasattr(file, 'filename'):
        return None
    if not file.filename:
        return None
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file.save(os.path.join(upload_folder, filename))
    return filename

def delete_file(filename, subfolder='projects'):
    """Supprime un fichier"""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

# --- Authentification ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nom d’utilisateur ou mot de passe incorrect', 'danger')
            return redirect(url_for('admin.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# --- Gestion des projets ---
@bp.route('/projects')
@login_required
def projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template('admin/projects.html', projects=projects)

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def project_new():
    form = ProjectForm()
    if form.validate_on_submit():
        # Créer un nouveau projet
        project = Project(
            titre=form.titre.data,
            description_courte=form.description_courte.data,
            description_longue=form.description_longue.data,
            lien_demo=form.lien_demo.data,
            lien_code=form.lien_code.data,
            date=form.date.data,
            client=form.client.data,
            categorie=form.categorie.data
        )
        # Gérer les technologies
        if form.technologies.data:
            project.set_technologies_list([t.strip() for t in form.technologies.data.split(',')])
        # Gérer l'image principale
        if form.image_principale.data:
            filename = save_file(form.image_principale.data, 'projects')
            if filename:
                project.image_principale = filename
        # Gérer les images secondaires (plusieurs)
        if form.images_secondaires.data:
            filenames = []
            for file in form.images_secondaires.data:
                if file:
                    fn = save_file(file, 'projects')
                    if fn:
                        filenames.append(fn)
            if filenames:
                project.set_images_secondaires_list(filenames)

        db.session.add(project)
        db.session.commit()
        flash('Projet ajouté avec succès.', 'success')
        return redirect(url_for('admin.projects'))
    return render_template('admin/project_form.html', form=form, project=None)

@bp.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def project_edit(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)  # pré-remplir avec les valeurs existantes
    if form.validate_on_submit():
        # Mettre à jour les champs
        project.titre = form.titre.data
        project.description_courte = form.description_courte.data
        project.description_longue = form.description_longue.data
        project.lien_demo = form.lien_demo.data
        project.lien_code = form.lien_code.data
        project.date = form.date.data
        project.client = form.client.data
        project.categorie = form.categorie.data

        if form.technologies.data:
            project.set_technologies_list([t.strip() for t in form.technologies.data.split(',')])
        else:
            project.technologies = None

        # Image principale : si nouvelle image, on remplace
        if form.image_principale.data:
            # Supprimer l'ancienne si elle n'est pas celle par défaut
            if project.image_principale and project.image_principale != 'default.jpg':
                delete_file(project.image_principale, 'projects')
            filename = save_file(form.image_principale.data, 'projects')
            if filename:
                project.image_principale = filename

        # Images secondaires : on ajoute les nouvelles (on ne supprime pas les anciennes automatiquement, à gérer)
        if form.images_secondaires.data:
            existing = project.get_images_secondaires_list()
            for file in form.images_secondaires.data:
                if file:
                    fn = save_file(file, 'projects')
                    if fn:
                        existing.append(fn)
            project.set_images_secondaires_list(existing)

        from werkzeug.datastructures import FileStorage

        if isinstance(form.image_principale.data, FileStorage) and form.image_principale.data:
            filename = save_file(form.image_principale.data, 'projects')
            if filename:
                project.image_principale = filename

        db.session.commit()
        flash('Projet modifié avec succès.', 'success')
        return redirect(url_for('admin.projects'))
    # Pré-remplir le champ technologies sous forme de chaîne
    if project.technologies:
        form.technologies.data = ', '.join(project.get_technologies_list())
    return render_template('admin/project_form.html', form=form, project=project)

@bp.route('/projects/delete/<int:id>', methods=['POST'])
@login_required
def project_delete(id):
    project = Project.query.get_or_404(id)
    # Supprimer les fichiers associés (sauf default.jpg)
    if project.image_principale and project.image_principale != 'default.jpg':
        delete_file(project.image_principale, 'projects')
    for img in project.get_images_secondaires_list():
        delete_file(img, 'projects')
    db.session.delete(project)
    db.session.commit()
    flash('Projet supprimé.', 'success')
    return redirect(url_for('admin.projects'))

# --- Gestion des services ---
@bp.route('/services')
@login_required
def services():
    from app.models import Service
    services = Service.query.order_by(Service.id).all()
    return render_template('admin/services.html', services=services)

@bp.route('/services/new', methods=['GET', 'POST'])
@login_required
def service_new():
    from app.models import Service
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            titre=form.titre.data,
            description=form.description.data,
            icone=form.icone.data,
            prix=form.prix.data
        )
        if form.features.data:
            service.set_features_list(form.features.data.split('\n'))
        db.session.add(service)
        db.session.commit()
        flash('Service ajouté avec succès.', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/service_form.html', form=form, service=None)

@bp.route('/services/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def service_edit(id):
    from app.models import Service
    service = Service.query.get_or_404(id)
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        service.titre = form.titre.data
        service.description = form.description.data
        service.icone = form.icone.data
        service.prix = form.prix.data
        if form.features.data:
            service.set_features_list(form.features.data.split('\n'))
        else:
            service.features = None
        db.session.commit()
        flash('Service modifié avec succès.', 'success')
        return redirect(url_for('admin.services'))
    # Pré-remplir le champ features
    if service.features:
        form.features.data = '\n'.join(service.get_features_list())
    return render_template('admin/service_form.html', form=form, service=service)

@bp.route('/services/delete/<int:id>', methods=['POST'])
@login_required
def service_delete(id):
    from app.models import Service
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    flash('Service supprimé.', 'success')
    return redirect(url_for('admin.services'))

# --- Gestion des témoignages ---
@bp.route('/testimonials')
@login_required
def testimonials():
    from app.models import Testimonial
    testimonials = Testimonial.query.order_by(Testimonial.date.desc()).all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

@bp.route('/testimonials/new', methods=['GET', 'POST'])
@login_required
def testimonial_new():
    from app.models import Testimonial
    form = TestimonialForm()
    if form.validate_on_submit():
        testimonial = Testimonial(
            auteur=form.auteur.data,
            fonction=form.fonction.data,
            message=form.message.data,
            note=form.note.data
        )
        if form.avatar.data:
            filename = save_file(form.avatar.data, 'testimonials')
            testimonial.avatar = filename
        db.session.add(testimonial)
        db.session.commit()
        flash('Témoignage ajouté.', 'success')
        return redirect(url_for('admin.testimonials'))
    return render_template('admin/testimonial_form.html', form=form, testimonial=None)

@bp.route('/testimonials/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def testimonial_edit(id):
    from app.models import Testimonial
    testimonial = Testimonial.query.get_or_404(id)
    form = TestimonialForm(obj=testimonial)
    if form.validate_on_submit():
        testimonial.auteur = form.auteur.data
        testimonial.fonction = form.fonction.data
        testimonial.message = form.message.data
        testimonial.note = form.note.data
        if form.avatar.data:
            # Supprimer ancien avatar si différent de default
            if testimonial.avatar and testimonial.avatar != 'default-avatar.jpg':
                delete_file(testimonial.avatar, 'testimonials')
            filename = save_file(form.avatar.data, 'testimonials')
            testimonial.avatar = filename
        db.session.commit()
        flash('Témoignage modifié.', 'success')
        return redirect(url_for('admin.testimonials'))
    return render_template('admin/testimonial_form.html', form=form, testimonial=testimonial)

@bp.route('/testimonials/delete/<int:id>', methods=['POST'])
@login_required
def testimonial_delete(id):
    from app.models import Testimonial
    testimonial = Testimonial.query.get_or_404(id)
    if testimonial.avatar and testimonial.avatar != 'default-avatar.jpg':
        delete_file(testimonial.avatar, 'testimonials')
    db.session.delete(testimonial)
    db.session.commit()
    flash('Témoignage supprimé.', 'success')
    return redirect(url_for('admin.testimonials'))

# --- Gestion de la bio ---
@bp.route('/bio', methods=['GET', 'POST'])
@login_required
def bio():
    from app.models import Bio
    bio = Bio.get_singleton()
    form = BioForm(obj=bio)
    if form.validate_on_submit():
        bio.nom = form.nom.data
        bio.titre = form.titre.data
        bio.localisation = form.localisation.data
        bio.email = form.email.data
        bio.disponible = form.disponible.data
        if form.bio_paragraphes.data:
            bio.set_bio_paragraphes_list(form.bio_paragraphes.data.split('\n'))
        else:
            bio.bio_paragraphes = None
        # Compétences : on les stocke en JSON
        competences = {}
        if form.competences_langages.data:
            competences['langages'] = [c.strip() for c in form.competences_langages.data.split(',')]
        if form.competences_frameworks.data:
            competences['frameworks'] = [c.strip() for c in form.competences_frameworks.data.split(',')]
        if form.competences_outils.data:
            competences['outils'] = [c.strip() for c in form.competences_outils.data.split(',')]
        bio.competences = competences
        # Avatar
        if form.avatar.data:
            # Supprimer ancien si différent de default
            if bio.avatar and bio.avatar != 'avatar.jpg':
                delete_file(bio.avatar, '')  # dans uploads/ directement
            filename = save_file(form.avatar.data, '')
            bio.avatar = filename
        db.session.commit()
        flash('Bio mise à jour.', 'success')
        return redirect(url_for('admin.bio'))
    # Pré-remplir les champs de compétences
    if bio.competences:
        form.competences_langages.data = ', '.join(bio.competences.get('langages', []))
        form.competences_frameworks.data = ', '.join(bio.competences.get('frameworks', []))
        form.competences_outils.data = ', '.join(bio.competences.get('outils', []))
    if bio.bio_paragraphes:
        form.bio_paragraphes.data = '\n'.join(bio.get_bio_paragraphes_list())
    return render_template('admin/bio.html', form=form, bio=bio)