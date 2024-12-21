from flask import jsonify,Response, request
import openai
from app.models import Feedback
import os
from dotenv import load_dotenv
from flask import render_template, request, redirect, url_for, flash
from app.models import Participant, db

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def admin_dashboard():
    """Tableau de bord principal."""
    return render_template('admin/dashboard.html')

def manage_participants():
    """Gère les participants."""
    if request.method == 'POST':
        # Ajouter un participant
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        sexe = request.form.get('sexe')
        age = request.form.get('age')
        profession = request.form.get('profession')

        try:
            participant = Participant(
                nom=nom,
                prenom=prenom,
                email=email,
                sexe=sexe,
                age=int(age) if age else None,
                profession=profession
            )
            db.session.add(participant)
            db.session.commit()
            flash("Participant ajouté avec succès.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", "danger")

        return redirect(url_for('manage_participants'))

    # Récupérer tous les participants
    participants = Participant.query.all()
    return render_template('admin/participants.html', participants=participants)

def check_auth(username, password):
    return username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD")

def authenticate():
    return Response(
        "Authentification requise", 401,
        {"WWW-Authenticate": "Basic realm='Login Required'"}
    )

def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def admin_feedback_summary():
    try:
        # Récupérer tous les feedbacks avec SQLAlchemy
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

        # Préparer les retours pour l'analyse globale
        feedback_texts = " ".join([f.feedback_text for f in feedbacks])

        # Générer une analyse globale avec GPT
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en analyse de feedback pour les événements."},
                {"role": "user", "content": f"Voici les retours des participants : {feedback_texts}. "
                                             f"Analysez-les pour fournir un sentiment global, les points forts et les points à améliorer."}
            ],
            max_tokens=500
        )
        summary = response.choices[0].message.content.strip()

        return render_template("admin_feedback_summary.html", summary=summary, feedbacks=feedbacks)

    except Exception as e:
        return render_template("error.html", error=str(e)), 500