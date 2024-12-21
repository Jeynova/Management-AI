import os
from flask import jsonify, request
import openai
from app.models import Participant, Speaker, Conference, db
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_full_conference():
    """Génère une conférence complète avec des données existantes ou GPT."""
    try:
        # Vérifier s'il y a des speakers existants dans la base
        speakers = Speaker.query.all()
        if not speakers:
            # Générer un speaker avec GPT si aucun n'existe
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un expert en génération de données pour une conférence."},
                    {"role": "user", "content": "Génère un conférencier pour une conférence d'intelligence artificielle."}
                ],
                max_tokens=100
            )
            speaker_data = response.choices[0].message.content.strip().split(", ")
            speaker = Speaker(
                nom=speaker_data[0],
                prenom=speaker_data[1],
                age=random.randint(30, 60),
                sexe="Femme" if random.choice([True, False]) else "Homme",
                profession="Conférencier spécialisé en IA"
            )
            db.session.add(speaker)
            db.session.flush()
        else:
            # Utiliser un speaker existant aléatoire
            speaker = random.choice(speakers)

        # Vérifier s'il y a des participants existants dans la base
        participants = Participant.query.all()
        new_participants = []
        if not participants:
            # Générer 10 participants avec GPT si aucun n'existe
            for i in range(10):
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en génération de données pour une conférence."},
                        {"role": "user", "content": "Génère un participant pour une conférence sur l'intelligence artificielle."}
                    ],
                    max_tokens=100
                )
                participant_data = response.choices[0].message.content.strip().split(", ")
                participant = Participant(
                    email=f"participant{i}@example.com",
                    nom=participant_data[0],
                    prenom=participant_data[1],
                    sexe="Femme" if i % 2 == 0 else "Homme",
                    age=random.randint(18, 60),
                    profession="Profession aléatoire"
                )
                db.session.add(participant)
                new_participants.append(participant)
        else:
            # Utiliser les participants existants
            new_participants = random.sample(participants, min(len(participants), 10))

        # Générer une conférence
        conference = Conference(
            theme="Les tendances de l'IA en 2024",
            speaker_id=speaker.id,
            horaire=datetime.utcnow() + timedelta(days=7)  # Conférence prévue dans 7 jours
        )
        db.session.add(conference)
        db.session.flush()

        # Associer les participants à la conférence
        for participant in new_participants:
            conference.participants.append(participant)

        # Générer une description pour la conférence via GPT
        description_prompt = f"""
        Génère une description captivante pour une conférence sur le thème suivant : 
        « {conference.theme} ». Le conférencier est {speaker.prenom} {speaker.nom}, spécialiste en {speaker.profession}. 
        La conférence accueillera {len(new_participants)} participants d'origines diverses.
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un expert en rédaction de descriptions pour des événements."},
                {"role": "user", "content": description_prompt}
            ],
            max_tokens=300
        )
        conference.description = response.choices[0].message.content.strip()
        db.session.commit()

        return jsonify({
            "message": "Conférence générée avec succès.",
            "conference": {
                "id": conference.id,
                "theme": conference.theme,
                "speaker": f"{speaker.prenom} {speaker.nom}",
                "horaire": conference.horaire,
                "participants": [f"{p.prenom} {p.nom}" for p in conference.participants]
            }
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Erreur lors de la génération de la conférence", "details": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def generate_mockup_dataset():
    """Génère un jeu de données fictif."""
    try:
        # Supprimer les données existantes (optionnel, pour éviter les doublons)
        db.session.query(Participant).delete()
        db.session.query(Speaker).delete()
        db.session.query(Conference).delete()

        # Générer des speakers
        speakers = []
        for i in range(5):
            speaker = Speaker(
                nom=f"NomSpeaker{i}",
                prenom=f"PrénomSpeaker{i}",
                age=random.randint(30, 60),
                sexe="Homme" if i % 2 == 0 else "Femme",
                profession="Expert en IA"
            )
            db.session.add(speaker)
            speakers.append(speaker)

        db.session.flush()  # Pour obtenir les IDs des speakers

        # Générer des conférences
        conferences = []
        for i in range(5):
            conference = Conference(
                theme=f"Thème de Conférence {i}",
                speaker_id=random.choice(speakers).id,
                horaire=datetime.utcnow() + timedelta(days=random.randint(1, 30))
            )
            db.session.add(conference)
            conferences.append(conference)

        # Générer des participants
        participants = []
        for i in range(20):
            participant = Participant(
                email=f"participant{i}@example.com",
                nom=f"Nom de personne fictif",
                prenom=f"Prénom de personne fictif",
                sexe="Homme" if i % 2 == 0 else "Femme",
                age=random.randint(18, 60),
                profession="Profession aléatoire"
            )
            db.session.add(participant)
            participants.append(participant)

        # Associer aléatoirement les participants aux conférences
        for participant in participants:
            conference = random.choice(conferences)
            conference.participants.append(participant)

        db.session.commit()

        return jsonify({
            "message": "Jeu de données fictif généré avec succès.",
            "speakers": [f"{s.prenom} {s.nom}" for s in speakers],
            "conferences": [c.theme for c in conferences],
            "participants": [f"{p.prenom} {p.nom}" for p in participants]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def generate_session_description():
    """
    Générer une description de session basée sur un thème et des mots-clés.
    """
    try:
        data = request.json
        theme = data.get("theme")
        keywords = data.get("keywords", "")
        conference_id = data.get("conference_id", None)

        if not theme:
            return jsonify({"error": "Le thème est requis pour générer une description."}), 400

        # Utiliser OpenAI pour générer la description
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = f"""
        Vous êtes un expert en rédaction pour des conférences. Voici le thème : {theme}.
        {f"Mots-clés : {keywords}." if keywords else ""}
        Rédigez une description claire et attrayante pour cette session.
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant spécialisé en rédaction de descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        description = response.choices[0].message.content.strip()

        # Si une conférence est spécifiée, mettre à jour la base de données
        if conference_id:
            conference = Conference.query.get(conference_id)
            if not conference:
                return jsonify({"error": "La conférence spécifiée n'existe pas."}), 404
            conference.theme = theme  # Si le thème doit être mis à jour
            conference.description = description
            db.session.commit()

        return jsonify({
            "theme": theme,
            "keywords": keywords,
            "description": description,
            "conference_id": conference_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
