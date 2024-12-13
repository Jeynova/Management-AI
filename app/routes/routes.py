from flask import render_template,jsonify
from app.controllers.home_controller import home
from app.models import Feedback, Participant, Speaker, Conference

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

def initialize_routes(app):
    """Ajout des routes spécifiques non couvertes par Flask-Admin."""
    app.add_url_rule('/api/feedbacks', 'get_feedbacks', get_feedbacks, methods=['GET'])
    app.add_url_rule('/', 'home', home, methods=['GET'])
    app.add_url_rule('/chat', 'chat', chat, methods=['GET'])

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
    return render_template('chat.html')
