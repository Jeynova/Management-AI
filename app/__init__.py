from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_talisman import Talisman
import os

db = SQLAlchemy()
migrate = Migrate()
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

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)

    # Secure configuration for production
    if os.getenv('FLASK_ENV') == 'production':
        Talisman(app)
    
    # Register Flask-Admin models dynamically
    from app.models import Feedback, Participant, Speaker, Conference, Visual, Evenement

    admin.add_view(ModelView(Feedback, db.session))
    admin.add_view(ModelView(Participant, db.session))
    admin.add_view(ModelView(Speaker, db.session))
    admin.add_view(ModelView(Visual, db.session))
    admin.add_view(ModelView(Evenement, db.session))

    # Register routes
    from app.routes.routes import initialize_routes
    initialize_routes(app)

    return app