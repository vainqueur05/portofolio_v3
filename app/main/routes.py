from flask import render_template, request, redirect
from app.main import bp
from app.models import Bio

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/about')
def about():
    about = Bio.get_singleton()
    return render_template('about.html', about=about)

from app.models import Project

@bp.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template('projects.html',projects=projects)

@bp.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)

from app.models import Service

@bp.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Rediriger vers Formspree avec les données
        return redirect('https://formspree.io/f/xaqpnkek', code=307)
    return render_template('contact.html')