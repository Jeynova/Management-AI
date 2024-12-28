import json
from app.models import Article, Conference, Evenement, Feedback
from app import db
import openai
from flask import flash, jsonify, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta

def submit_feedback():
    """Handles the submission of feedback."""
    try:
        # Récupérer les données du formulaire
        data = request.json
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        feedback_text = data.get("feedback", "").strip()
        event_id = data.get("event_id")
        conference_id = data.get("conference_id")

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
            sentiment=sentiment,
            evenement_id=event_id,
            conference_id=conference_id
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

        # Générer un résumé et des points à améliorer avec GPT
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant spécialisé en analyse de feedback."},
                {"role": "user", "content": f"""
                    Analyse les retours suivants et génère :
                    1. Un résumé des points positifs.
                    2. Une liste des points à améliorer.
                    Voici les retours :
                    {feedback_texts}
                """}
            ],
            max_tokens=300
        )
        summary = response.choices[0].message.content.strip()

        # Exemple d'envoi vers un pipeline Pipedream
        pipedream_url = os.getenv("PIPEDREAM_URL")
        pipedream_payload = {
            "summary": summary,
            "total_feedbacks": total_feedbacks,
            "positive": positive,
            "negative": negative,
            "ratio": ratio
        }
        if pipedream_url:
            requests.post(pipedream_url, json=pipedream_payload)

        return {
            "total_feedbacks": total_feedbacks,
            "positive": positive,
            "negative": negative,
            "ratio": ratio,
            "summary": summary
        }
    except Exception as e:
        return {"error": str(e)}
    
def generate_random_feedbacks(conferences, participants, number=10):
    """Génère des feedbacks aléatoires pour des conférences."""
    try:
        feedbacks = []
        for _ in range(number):
            participant = random.choice(participants)
            conference = random.choice(conferences)

            feedback_text = f"C'était une super conférence sur {conference.theme} ! Merci à {conference.speaker.prenom}."
            sentiment = "positif" if random.random() > 0.5 else "négatif"

            feedback = Feedback(
                participant_name=f"{participant.prenom} {participant.nom}",
                participant_email=participant.email,
                feedback_text=feedback_text,
                sentiment=sentiment,
                conference_id=conference.id
            )
            db.session.add(feedback)
            feedbacks.append(feedback)

        db.session.commit()
        return feedbacks
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erreur lors de la génération des feedbacks : {str(e)}")