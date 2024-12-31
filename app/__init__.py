from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_talisman import Talisman
import os
from flask_mail import Mail
from streamlit import feedback

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()  # Instanciation de Flask-Mail
admin = Admin(template_mode='bootstrap4')

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.config.Config')
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@"
        f"{app.config['MYSQL_HOST']}/{app.config['MYSQL_DATABASE']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Configuration et extensions
    app.config.from_object('config.config.Config')
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    mail.init_app(app)

    from app.services.listener import sql_listener
    # Secure configuration for production
    if os.getenv('FLASK_ENV') == 'production':
        Talisman(app)
    
     # Enregistrer les modèles pour Flask-Admin avec des noms uniques
    from app.models import Feedback, Participant, Speaker, Conference, Visual, Evenement

    """ admin.add_view(ModelView(Feedback, db.session, endpoint="admin_feedback"))
    admin.add_view(ModelView(Participant, db.session, endpoint="admin_participant"))
    admin.add_view(ModelView(Speaker, db.session, endpoint="admin_speaker"))
    admin.add_view(ModelView(Conference, db.session, endpoint="admin_conference"))
    admin.add_view(ModelView(Visual, db.session, endpoint="admin_visual"))
    admin.add_view(ModelView(Evenement, db.session, endpoint="admin_event"))
 """
    # Routes
    from app.routes.routes import initialize_routes
    initialize_routes(app)
    
    return app