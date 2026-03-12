# init_db.py
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Crée toutes les tables
    db.create_all()
    print("✅ Tables créées avec succès !")
    
    # Vérifie si un admin existe déjà pour éviter les doublons
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')  # 🔑 N'oublie pas de changer ce mot de passe plus tard !
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin créé : admin / admin123")
    else:
        print("ℹ️ L'admin existe déjà, aucune action.")