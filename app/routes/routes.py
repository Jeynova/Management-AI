from flask import flash, redirect, render_template, jsonify, request, url_for
from app.controllers.home_controller import home
from app.controllers.visual_controller import (
    generate_visual,
    iterate_visual,
)
from app.models import Feedback, Participant, Speaker, Conference, Visual
from app.controllers.speaker_controller import (
    generate_biography,
    generate_biographies_bulk,
    regenerate_biography
)
from app.controllers.conference_controller import (
    generate_session_description,
    generate_full_conference,
    generate_mockup_dataset
)
from app.controllers.article_controller import generate_article

def get_feedbacks():
    """Récupère tous les feedbacks pour une API."""
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


def initialize_routes(app):
    """Ajout des routes spécifiques non couvertes par Flask-Admin."""
    # Route principale
    app.add_url_rule('/', 'home', home, methods=['GET'])

    # API pour récupérer les feedbacks
    app.add_url_rule('/api/feedbacks', 'get_feedbacks', get_feedbacks, methods=['GET'])

    # Chat dynamique (HTML ou autre interface)
    app.add_url_rule('/chat', 'chat', chat, methods=['GET'])

    # Génération IA : description de session
    app.add_url_rule('/api/generate-session-description', 'generate_session_description', generate_session_description, methods=['POST'])

    # Génération IA : création complète d'une conférence
    app.add_url_rule('/api/generate-full-conference', 'generate_full_conference', generate_full_conference, methods=['POST'])

    # Génération IA : création d'un jeu de données mockup
    app.add_url_rule('/api/generate-mockup-dataset', 'generate_mockup_dataset', generate_mockup_dataset, methods=['POST'])

    # Génération IA : création de biographies pour les speakers
    app.add_url_rule('/api/speakers/<int:speaker_id>/generate-bio', 'generate_biography', generate_biography, methods=['POST'])
    app.add_url_rule('/api/speakers/generate-bios', 'generate_biographies_bulk', generate_biographies_bulk, methods=['POST'])
    app.add_url_rule('/api/speakers/<int:speaker_id>/regenerate-bio', 'regenerate_biography', regenerate_biography, methods=['POST'])

    # Génération IA : création d'article en fonction d'une conférence
    app.add_url_rule('/api/generate-article', 'generate_article', generate_article, methods=['POST'])

    # API pour la génération de visuels
    app.add_url_rule('/api/generate-visual', 'generate_visual', generate_visual, methods=['POST'])
    app.add_url_rule('/api/iterate-visual', 'iterate_visual', iterate_visual, methods=['POST'])

    # Affichage des données dans des tables
    @app.route('/tables', methods=['GET'])
    def display_tables():
        participants = Participant.query.all()
        speakers = Speaker.query.all()
        conferences = Conference.query.all()

        # Construction des données pour l'affichage
        conferences_with_participants = []
        for conference in conferences:
            speaker = Speaker.query.get(conference.speaker_id)
            conference_data = {
                'id': conference.id,
                'theme': conference.theme,
                'horaire': conference.horaire,
                'speaker': f"{speaker.prenom} {speaker.nom}" if speaker else "Non spécifié",
                'participants': [
                    f"{p.prenom} {p.nom}" for p in conference.participants
                ]
            }
            conferences_with_participants.append(conference_data)

        return render_template(
            'tables.html',
            participants=participants,
            speakers=speakers,
            conferences=conferences_with_participants
        )

def chat():
    """Affiche l'interface de chat."""
    return render_template('chat.html')
