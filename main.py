from app import create_app
from flask import send_from_directory

app = create_app()


@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir les fichiers statiques."""
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(debug=True)