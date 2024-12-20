import os
import json
from datetime import datetime
from sqlalchemy import and_
import sys
import logging

# Ajouter le chemin racine du projet
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import Participant, Speaker, Conference


# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

def load_test_data():
    app = create_app()
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/test_data.json'))

    logger.info(f"Chargement des données depuis : {data_file}")

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Erreur : fichier {data_file} introuvable.")
        return

    with app.app_context():
        logger.info("Ajout des participants...")
        existing_participants = {p.email for p in Participant.query.all()}
        for participant_data in data.get('participants', []):
            if participant_data["email"] not in existing_participants:
                try:
                    participant = Participant(**participant_data)
                    db.session.add(participant)
                except Exception as e:
                    logger.error(f"Erreur pour le participant {participant_data['email']}: {e}")

        logger.info("Ajout des speakers...")
        existing_speakers = {(s.nom, s.prenom) for s in Speaker.query.all()}
        for speaker_data in data.get('speakers', []):
            if (speaker_data["nom"], speaker_data["prenom"]) not in existing_speakers:
                try:
                    speaker = Speaker(**speaker_data)
                    db.session.add(speaker)
                except Exception as e:
                    logger.error(f"Erreur pour le speaker {speaker_data['nom']}: {e}")

        logger.info("Ajout des conférences...")
        existing_conferences = {(c.theme, c.speaker_id) for c in Conference.query.all()}
        for conference_data in data.get('conferences', []):
            if (conference_data["theme"], conference_data["speaker_id"]) not in existing_conferences:
                try:
                    horaire = datetime.fromisoformat(conference_data["horaire"])
                    conference = Conference(
                        theme=conference_data["theme"],
                        speaker_id=conference_data["speaker_id"],
                        horaire=horaire,
                        description=conference_data["description"]
                    )
                    db.session.add(conference)
                except Exception as e:
                    logger.error(f"Erreur pour la conférence {conference_data['theme']}: {e}")

        try:
            db.session.commit()
            logger.info("Données de test chargées avec succès.")
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Erreur lors du commit des données : {e}")

if __name__ == "__main__":
    load_test_data()
