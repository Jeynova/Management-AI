from flask import jsonify, request, render_template
import openai
import os
from app.models import Feedback, db  # Import SQLAlchemy models

def render_feedback_form():
    """Renders the feedback form."""
    return render_template('feedback_form.html')


def submit_feedback():
    """Handles the submission of feedback."""
    try:
        # Récupérer les données du formulaire
        data = request.json
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        feedback_text = data.get("feedback", "").strip()

        # Vérifications des données
        if not name or not feedback_text:
            return jsonify({"error": "Le nom et le retour sont obligatoires."}), 400

        # Analyse du sentiment avec GPT
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en analyse de sentiment."},
                {"role": "user", "content": f"Déterminez le sentiment de ce retour : {feedback_text}"}
            ],
            max_tokens=50
        )
        sentiment = response.choices[0].message.content.strip()

        # Enregistrer le feedback dans la base de données
        feedback = Feedback(
            participant_name=name,
            participant_email=email,
            feedback_text=feedback_text,
            sentiment=sentiment
        )
        db.session.add(feedback)
        db.session.commit()

        return jsonify({"message": "Feedback enregistré avec succès.", "sentiment": sentiment})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def analyze_feedbacks():
    """Provides a summary of all feedbacks."""
    try:
        # Récupérer tous les feedbacks
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

        # Préparer les textes pour l'analyse
        feedback_texts = " ".join([fb.feedback_text for fb in feedbacks])

        # Générer un résumé avec GPT
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant spécialisé en analyse de feedback."},
                {"role": "user", "content": f"Générez un résumé des points clés des retours suivants : {feedback_texts}"}
            ],
            max_tokens=300
        )
        summary = response.choices[0].message.content.strip()

        # Retourner le résumé et les feedbacks
        return jsonify({
            "feedbacks": [
                {
                    "id": fb.id,
                    "name": fb.participant_name,
                    "email": fb.participant_email,
                    "feedback": fb.feedback_text,
                    "sentiment": fb.sentiment,
                    "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M:%S")
                } for fb in feedbacks
            ],
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500