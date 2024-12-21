from flask import jsonify, request, render_template
import openai
import os
from app.models import Feedback, db
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

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


def analyze_feedbacks(start_time=None, end_time=None):
    """Provides a summary of feedbacks, optionally within a date range."""
    try:
        # Déterminer la plage de dates
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(days=1)
        if end_time is None:
            end_time = datetime.utcnow()

        # Récupérer les feedbacks dans la plage de dates
        feedbacks = Feedback.query.filter(
            Feedback.created_at >= start_time,
            Feedback.created_at <= end_time
        ).order_by(Feedback.created_at.desc()).all()

        # Préparer les textes pour l'analyse
        feedback_texts = " ".join([fb.feedback_text for fb in feedbacks])
        total_feedbacks = len(feedbacks)

        if not feedback_texts:
            return {
                "total_feedbacks": 0,
                "positive": 0,
                "negative": 0,
                "ratio": "0:0",
                "summary": "Aucun feedback trouvé pour cette période."
            }

        # Calcul du ratio positif/négatif
        positive = sum(1 for fb in feedbacks if "positif" in fb.sentiment.lower())
        negative = total_feedbacks - positive
        ratio = f"{positive}:{negative}"

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

        return {
            "total_feedbacks": total_feedbacks,
            "positive": positive,
            "negative": negative,
            "ratio": ratio,
            "summary": summary
        }
    except Exception as e:
        return {"error": str(e)}