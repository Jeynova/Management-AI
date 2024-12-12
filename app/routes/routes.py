from app.controllers.faq_controller import faq
from app.controllers.register_controller import register
from app.controllers.report_controller import report
from app.controllers.home_controller import home
from app.controllers.generate_controller import generate
from app.controllers.feedback_controller import analyze_feedbacks
from app.controllers.faq_controller import faq, add_faq, delete_faq
from app.controllers.feedback_controller import render_feedback_form, submit_feedback
from app.controllers.admin_controller import admin_feedback_summary
from flask import jsonify, json,render_template
from app.models import Feedback, Participant, Speaker, Conference
from app import db
import random
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def get_feedbacks():
    try:
        feedbacks = Feedback.query.all()
        feedback_list = [
            {
                "participant_name": f.participant_name,
                "participant_email": f.participant_email,
                "feedback_text": f.feedback_text,
                "sentiment": f.sentiment,
                "created_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for f in feedbacks
        ]
        return jsonify(feedbacks=feedback_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def add_random_elements():
    try:
        # Charger les données de test
        with open("data/test_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        added_elements = []

        # Ajouter les participants
        for participant_data in data["participants"]:
            try:
                participant = Participant(
                    email=participant_data["email"],
                    nom=participant_data["nom"],
                    prenom=participant_data["prenom"],
                    sexe=participant_data.get("sexe"),
                    age=participant_data.get("age"),
                    profession=participant_data["profession"]
                )
                db.session.add(participant)
                db.session.flush()  # Obtenir l'ID sans commit complet
                added_elements.append(f"Participant ajouté : {participant.nom} {participant.prenom}")
            except IntegrityError:
                db.session.rollback()  # Ignorer les doublons
                added_elements.append(f"Participant existant : {participant_data['email']}")

        # Ajouter les speakers
        for speaker_data in data["speakers"]:
            speaker = Speaker(
                nom=speaker_data["nom"],
                prenom=speaker_data["prenom"],
                age=speaker_data.get("age"),
                sexe=speaker_data.get("sexe"),
                profession=speaker_data["profession"]
            )
            db.session.add(speaker)
            db.session.flush()
            added_elements.append(f"Speaker ajouté : {speaker.nom} {speaker.prenom}")

        # Obtenir la liste des speaker IDs valides
        speaker_ids = [speaker.id for speaker in Speaker.query.all()]

        # Ajouter les conférences
        for conference_data in data["conferences"]:
            try:
                # Si aucun speaker_id n'est défini ou invalide, assigner un speaker aléatoire
                speaker_id = conference_data.get("speaker_id")
                if not speaker_id or speaker_id not in speaker_ids:
                    speaker_id = random.choice(speaker_ids)

                conference = Conference(
                    theme=conference_data["theme"],
                    speaker_id=speaker_id,
                    horaire=conference_data["horaire"]
                )
                db.session.add(conference)
                db.session.flush()
                added_elements.append(f"Conférence ajoutée : {conference.theme} avec Speaker ID {speaker_id}")
            except IntegrityError:
                db.session.rollback()  # Ignorer les erreurs
                added_elements.append(f"Erreur lors de l'ajout de la conférence : Speaker ID {conference_data.get('speaker_id', 'N/A')} non valide")

        # Ajouter des relations entre participants et conférences
        for _ in range(5):  # Ajouter 5 relations aléatoires
            participant = random.choice(Participant.query.all())
            conference = random.choice(Conference.query.all())
            if conference not in participant.conferences:
                participant.conferences.append(conference)
                added_elements.append(f"Participant {participant.nom} assigné à la conférence {conference.theme}")

        # Commit final
        db.session.commit()
        return jsonify({"message": "Ajout aléatoire effectué", "added": added_elements}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def initialize_routes(app):
    app.add_url_rule('/', 'home', home, methods=['GET'])
    app.add_url_rule('/faq', 'faq', faq, methods=['GET', 'POST'])
    app.add_url_rule('/faq/add', 'add_faq', add_faq, methods=['POST'])
    app.add_url_rule('/faq/delete', 'delete_faq', delete_faq, methods=['DELETE'])
    app.add_url_rule('/register', 'register', register, methods=['POST'])
    app.add_url_rule('/report', 'report', report, methods=['GET'])
    app.add_url_rule('/generate', 'generate', generate, methods=['POST'])
    app.add_url_rule('/feedback/analyze', 'analyze_feedbacks', analyze_feedbacks, methods=['POST'])
    app.add_url_rule('/feedback', 'render_feedback_form', render_feedback_form, methods=['GET'])
    app.add_url_rule('/feedback/submit', 'submit_feedback', submit_feedback, methods=['POST'])
    app.add_url_rule('/admin/feedback-summary', 'admin_feedback_summary', admin_feedback_summary, methods=['GET'])
    app.add_url_rule('/add-random', 'add_random_elements', add_random_elements, methods=['GET', 'POST'])
    app.add_url_rule('/api/feedbacks', 'get_feedbacks', get_feedbacks, methods=['GET'])
    
       # Route pour afficher les données des tables
    @app.route('/tables', methods=['GET'])
    def display_tables():
        participants = Participant.query.all()
        speakers = Speaker.query.all()
        conferences = Conference.query.all()

    # Ajouter les participants à chaque conférence
        conferences_with_participants = []
        for conference in conferences:
            speaker = Speaker.query.get(conference.speaker_id)
            conference_data = {
                'id': conference.id,
                'theme': conference.theme,
                'speaker_id': conference.speaker_id,
                'horaire': conference.horaire,
                'participants': conference.participants,
                'speaker': {
                    'nom': speaker.nom,
                    'prenom': speaker.prenom
                } if speaker else None
            }
            conferences_with_participants.append(conference_data)

        return render_template('tables.html', participants=participants, speakers=speakers, conferences=conferences_with_participants)
