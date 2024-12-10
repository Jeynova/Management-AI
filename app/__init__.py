from flask import Flask, jsonify
from flask_mysqldb import MySQL

# Initialize MySQL globally
mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.config.Config')
    
    # Initialize MySQL
    mysql.init_app(app)
    
    # Delay the import of routes to avoid circular imports
    from app.routes.routes import initialize_routes
    initialize_routes(app)
    
    # Test Route for DB Connectivity
    @app.route('/test-db')
    def test_db():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            cursor.close()
            return jsonify({"tables": [table[0] for table in tables]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app