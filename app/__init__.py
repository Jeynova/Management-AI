from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text

# Initialize SQLAlchemy and Flask-Migrate globally
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration from config file
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

    # Import and initialize routes
    from app.routes.routes import initialize_routes
    initialize_routes(app)

    # Test route for debugging database connection
    @app.route('/test-db')
    def test_db():
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]
            return {
                "tables": tables
            }
        except Exception as e:
            return {"error": str(e)}, 500
    return app