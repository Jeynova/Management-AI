from flask import render_template, request, redirect, url_for, flash
from app.models import Evenement, db
from datetime import datetime
from app.models import Evenement, Speaker, Participant, Conference, Visual, Feedback


def list_events():
    """Affiche la liste des événements."""
    events = Evenement.query.order_by(Evenement.date.desc()).all()
    return render_template('events/index.html',page_name='events', events=events)

def create_event():
    """Crée un nouvel événement."""
    if request.method == 'POST':
        titre = request.form.get('titre')
        date = request.form.get('date')
        description = request.form.get('description')

        if not titre or not date:
            flash("Le titre et la date sont obligatoires.", "danger")
            return redirect(url_for('create_event_form'))

        try:
            # Création de l'événement
            event = Evenement(titre=titre, date=date, description=description)
            db.session.add(event)
            db.session.commit()

            flash("Événement créé avec succès.", "success")
            # Redirection vers la gestion de l'événement
            return redirect(url_for('manage_event', event_id=event.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la création de l'événement : {str(e)}", "danger")
            print(f"Erreur : {str(e)}")  # Affichez l'erreur dans la console pour débogage
            return redirect(url_for('create_event'))

    return render_template('events/create.html')

def manage_event(event_id):
    """Affiche la page de gestion pour un événement."""
    event = Evenement.query.get_or_404(event_id)

    # Récupérer les données associées
    # Récupérer les speakers via les conférences associées à l'événement
    speakers = Speaker.query.join(Conference).filter(Conference.evenement_id == event.id).all()
    participants = Participant.query.filter(Participant.conferences.any(evenement_id=event.id)).all()
    conferences = Conference.query.filter_by(evenement_id=event.id).all()
    visuals = Visual.query.filter_by(evenement_id=event.id).all()
    feedbacks = Feedback.query.filter_by(evenement_id=event.id).all()

    return render_template(
        'events/manage.html',
        event=event,
        speakers=speakers,
        participants=participants,
        conferences=conferences,
        visuals=visuals,
        feedbacks=feedbacks,
        page_name='events'
    )