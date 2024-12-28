import json
from app.models import Conference, Evenement, Participant, Speaker
from app import db
import openai
from flask import jsonify
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta



load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_conferences_for_event(event_id, number=3):
    """Génère des conférences pour un événement spécifique."""
    try:
        # Récupérer l'événement
        event = Evenement.query.get(event_id)
        if not event:
            return jsonify({"error": "Événement non trouvé."}), 404

        # Vérifier la disponibilité des speakers
        speakers = Speaker.query.all()
        if len(speakers) < number:
            return jsonify({"error": "Pas assez d'orateurs disponibles pour générer les conférences."}), 400

        # Récupérer les participants disponibles
        participants = Participant.query.all()
        if not participants:
            return jsonify({"error": "Aucun participant disponible pour les conférences."}), 400

        # Sélectionner des speakers aléatoires sans répétition
        selected_speakers = random.sample(speakers, number)

        conferences = []
        for speaker in selected_speakers:
            # Générer un thème basé sur la spécialité du speaker
            theme_prompt = f"""
            Propose un thème captivant pour une conférence donnée par {speaker.prenom} {speaker.nom}, 
            expert en {speaker.profession}. Le thème doit être spécifique à son domaine d'expertise.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un event planner professionnel et createur de thèmes pour des conférences professionnelles."},
                    {"role": "user", "content": theme_prompt}
                ],
                max_tokens=100
            )
            theme = response.choices[0].message.content.strip()

            # Générer une description pour la conférence
            description_prompt = f"""
            Génère une description captivante pour une conférence intitulée « {theme} ».
            Cette conférence sera donnée par {speaker.prenom} {speaker.nom}, un expert en {speaker.profession}.
            Décris pourquoi ce thème est important et ce que les participants apprendront.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un rédacteur expert en descriptions de conférences."},
                    {"role": "user", "content": description_prompt}
                ],
                max_tokens=200
            )
            description = response.choices[0].message.content.strip()

            # Créer la conférence
            conference = Conference(
                theme=theme,
                speaker_id=speaker.id,
                horaire=datetime.utcnow() + timedelta(days=random.randint(1, 30)),  # Date aléatoire dans les 30 prochains jours
                description=description,
                evenement_id=event.id
            )
            db.session.add(conference)
            db.session.flush()  # Obtenir l'ID de la conférence

            # Associer des participants aléatoires à la conférence
            conference_participants = random.sample(participants, min(len(participants), 10))
            for participant in conference_participants:
                conference.participants.append(participant)

            conferences.append(conference)

        # Sauvegarder toutes les conférences
        db.session.commit()

        return jsonify({
            "message": f"{len(conferences)} conférences générées avec succès.",
            "conferences": [
                {
                    "id": conf.id,
                    "theme": conf.theme,
                    "speaker": f"{conf.speaker.prenom} {conf.speaker.nom}",
                    "participants": [f"{p.prenom} {p.nom}" for p in conf.participants]
                } for conf in conferences
            ]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
