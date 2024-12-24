from flask import flash, redirect, render_template, jsonify, request, url_for
from app.controllers.home_controller import home
from app.controllers.visual_controller import (
    generate_visual,
    iterate_visual,
    manage_visuals
)
from app.models import Feedback, Participant, Speaker, Conference, Visual
from app.controllers.speaker_controller import (
    generate_biography,
    generate_biographies_bulk,
    regenerate_biography,
    manage_speakers
)
from app.controllers.conference_controller import (
    generate_session_description,
    generate_full_conference,
    generate_mockup_dataset,
    manage_conferences
)
from app.controllers.article_controller import generate_article
from app.controllers.data_controller import data_bp
from app.controllers.event_controller import (
    list_events,
    create_event,
    manage_event
)

from app.controllers.participants_controller import manage_participants, generate_random_participant

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

def data():
    return render_template('data.html')
    
def initialize_routes(app):
    """Ajout des routes spécifiques pour la gestion des projets et des entités associées."""
    # Route principale
    app.add_url_rule('/', 'home', home, methods=['GET'])

    # Projets
    app.add_url_rule('/projets', 'list_events', list_events, methods=['GET'])
    app.add_url_rule('/projets/nouveau', 'create_event', create_event, methods=['GET', 'POST'])
    app.add_url_rule('/projets/<int:event_id>/gestion', 'manage_event', manage_event, methods=['GET'])

    # Participants
    app.add_url_rule('/projets/<int:event_id>/participants', 'manage_participants', manage_participants, methods=['GET', 'POST'])
    app.add_url_rule('/projets/<int:event_id>/participants/random', 'generate_random_participant', generate_random_participant, methods=['POST'])

    # Conférenciers
    app.add_url_rule('/projets/<int:event_id>/speakers', 'manage_speakers', manage_speakers, methods=['GET', 'POST'])
    app.add_url_rule('/projets/<int:event_id>/speakers/generate', 'generate_biography', generate_biography, methods=['POST'])

    # Conférences
    app.add_url_rule('/projets/<int:event_id>/conferences', 'manage_conferences', manage_conferences, methods=['GET', 'POST'])
    app.add_url_rule('/projets/<int:event_id>/conferences/generate', 'generate_session_description', generate_session_description, methods=['POST'])

    # Visuels
    app.add_url_rule('/projets/<int:event_id>/visuels', 'manage_visuals', manage_visuals, methods=['GET', 'POST'])
    app.add_url_rule('/api/generate-visual', 'generate_visual', generate_visual, methods=['POST'])
    app.add_url_rule('/api/iterate-visual', 'iterate_visual', iterate_visual, methods=['POST'])

    # Analyse et marketing
    """ app.add_url_rule('/projets/<int:event_id>/analysis', 'analysis', analysis, methods=['GET'])
    app.add_url_rule('/projets/<int:event_id>/marketing', 'marketing', marketing, methods=['GET']) """

    # Feedbacks
    """ app.add_url_rule('/projets/<int:event_id>/feedbacks', 'manage_feedbacks', manage_feedbacks, methods=['GET', 'POST']) """

    # Chat dynamique (interface HTML)
    app.add_url_rule('/chat', 'chat', chat, methods=['GET'])

    # Tableau de bord admin
    """ app.add_url_rule('/admin', 'admin_dashboard', admin_dashboard, methods=['GET']) """

    # Enregistrement des autres API déjà présentes
    app.add_url_rule('/api/feedbacks', 'get_feedbacks', get_feedbacks, methods=['GET'])
    app.add_url_rule('/api/generate-random-participant', 'generate_random_participant', generate_random_participant, methods=['GET'])

    @app.route('/tables', methods=['GET'])
    def display_tables():
        participants = Participant.query.all()
        speakers = Speaker.query.all()
        conferences = Conference.query.all()

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
