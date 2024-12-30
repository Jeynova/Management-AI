import json
from app.models import Feedback
from app import db
import openai
from flask import jsonify, request
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta
import requests

load_dotenv()


def submit_feedback():
    """Handles the submission of feedback."""
    try:
        data = request.json
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        feedback_text = data.get("feedback", "").strip()
        event_id = data.get("event_id")
        conference_id = data.get("conference_id")

        if not name or not feedback_text:
            return jsonify({"error": "Le nom et le retour sont obligatoires."}), 400

        # Analyse du sentiment avec GPT
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en analyse de sentiment."},
                {"role": "user", "content": f"Déterminez le sentiment de ce retour : {feedback_text}"}
            ],
            max_tokens=50
        )
        sentiment = response.choices[0].message.content.strip()

        # Enregistrement en base
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
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(days=1)
        if end_time is None:
            end_time = datetime.utcnow()

        feedbacks = Feedback.query.filter(
            Feedback.created_at >= start_time,
            Feedback.created_at <= end_time
        ).order_by(Feedback.created_at.desc()).all()

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

        positive = sum(1 for fb in feedbacks if "positif" in fb.sentiment.lower())
        negative = total_feedbacks - positive
        ratio = f"{positive}:{negative}"

        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.chat.completions.create(
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
        if pipedream_url:
            requests.post(pipedream_url, json={
                "summary": summary,
                "total_feedbacks": total_feedbacks,
                "positive": positive,
                "negative": negative,
                "ratio": ratio
            })

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
    feedbacks = []
    try:
        for _ in range(number):
            conference = random.choice(conferences)
            participant = random.choice(participants)

            prompt = f"""
            Génère un feedback JSON structuré pour la conférence suivante :
            - Thème : {conference['theme']}
            - Conférencier : {conference['speaker']}
            - Nom du participant : {participant.prenom} {participant.nom}
            Retourne uniquement un JSON strictement formaté comme suit :
            {{
                "feedback_text": "Texte du feedback.",
                "sentiment": "positif" ou "négatif"
            }}
            """
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un générateur de feedbacks professionnels."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            raw_response = response.choices[0].message.content.strip()

            # Validation du JSON
            try:
                feedback_json = json.loads(raw_response)
                feedback = Feedback(
                    participant_name=f"{participant.prenom} {participant.nom}",
                    participant_email=participant.email,
                    feedback_text=feedback_json["feedback_text"],
                    sentiment=feedback_json["sentiment"],
                    conference_id=conference["id"]
                )
                db.session.add(feedback)
                feedbacks.append(feedback)
            except json.JSONDecodeError as e:
                print(f"Erreur de parsing JSON : {e}. Réponse brute : {raw_response}")

        db.session.commit()
        return feedbacks
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erreur lors de la génération des feedbacks : {str(e)}")