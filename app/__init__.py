from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
admin = Admin(name='Admin Dashboard', template_mode='bootstrap4')

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

    # Register Flask-Admin models dynamically
    from app.models import Feedback, Participant, Speaker, Conference
    from flask_admin.contrib.sqla import ModelView
    admin.add_view(ModelView(Feedback, db.session))
    admin.add_view(ModelView(Participant, db.session))
    admin.add_view(ModelView(Speaker, db.session))
    class ConferenceAdmin(ModelView):
        form_columns = ['theme', 'speaker_id', 'horaire', 'description']  # Ajout du champ description
        column_searchable_list = ['theme', 'description']
        column_filters = ['theme', 'horaire']

    admin.add_view(ConferenceAdmin(Conference, db.session))

    # Register routes
    from app.routes.routes import initialize_routes
    initialize_routes(app)

    @app.route('/test-db')
    def test_db():
        """Route for testing database connection."""
        from sqlalchemy import text
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]
            return {"tables": tables}
        except Exception as e:
            return {"error": str(e)}, 500

    return app
