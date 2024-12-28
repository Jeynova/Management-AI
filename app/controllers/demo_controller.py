from flask import jsonify, render_template, request, redirect, url_for, flash
from app.models import Evenement, db
from datetime import datetime
from app.models import Evenement, Speaker, Participant, Conference, Visual, Feedback
import openai
import os
from dotenv import load_dotenv
import pandas as pd
import json
import re
from datetime import datetime
from app.services.feedback_service import generate_random_feedbacks
from app.services.participant_service import generate_random_participants_with_gpt, save_participants_to_db
from app.services.speaker_service import generate_random_speakers_with_biographies, save_speakers_with_biographies_to_db
from app.services.conference_service import generate_conferences_for_event
from app.services.article_service import generate_articles
from app.services.visual_service import generate_event_visuals
from app.services.social_service import generate_social_posts


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def list_demo_events():
    """Affiche la liste des événements."""
    events = Evenement.query.order_by(Evenement.date.desc()).all()
    return render_template('demo/index.html',page_name='demo', events=events)

def create_demo_event():
    """Crée un nouvel événement."""
    prompt = f"""
        Tu es un rédacteur spécialisé en creation événementielle et gestion de projet.
        Je veux que tu génères un JSON structuré pour un article, sans texte additionnel en dehors du JSON. 
        Assure-toi que les chaînes de caractères soient correctement échappées. Voici les champs que je veux:
            - `title` : un titre d'evenement en rapport avec les nouvelles technologies simple et efficace en gardant en tête que nous somme le 27/12/2024. Exemple: The Next Web 2024, Cyber Security Global Summit,Big Data & AI Paris etc...
            - `date` : la date de preference au moins à partir d'1 mois après la date actuelle sous un format datetime compatible aux insertions sql.
            - `description` : Rédige une description captivante pour promouvoir l'evenement basé sur le titre trouvé plus haut. Ti devras adapter ton ton et le contenu en fonction du titre et du potentiel public visé ( professionnels, étudiants, grand public, etc.).
            - `theme` : le principal theme de l'evenement basé sur la description.
        Le JSON doit suivre ce format:
        {{
            "title": "Titre généré",
            "date": "date generée",
            "description": "description complete générée",
            "theme": "theme généré"
        }}
        Tu dois retourner un JSON FORMATTE CLAIR ET UTILISABLE.
        """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un rédacteur spécialisé en creation événementielle et gestion de projet."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        raw_response = response.choices[0].message.content.strip()
        print(f"raw_response : {raw_response}")

    except Exception as e:
        raise ValueError(f"Erreur inattendue lors de la génération de l'article : {str(e)}")
    try:
        # Parse the JSON directly
        event_json = json.loads(raw_response)

    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur lors de l'analyse du JSON généré par GPT: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Erreur: Clé manquante dans la réponse JSON: {str(e)}")

    """ event = Evenement(titre=title, date=date, description=description) """
    """ try:
        # Création de l'événement
        event = Evenement(titre=title, date=date, description=description)
        db.session.add(event)
        db.session.commit()

        flash("Événement créé avec succès.", "success")
        # Redirection vers la gestion de l'événement
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la création de l'événement : {str(e)}", "danger")
        print(f"Erreur : {str(e)}")  # Affichez l'erreur dans la console pour débogage """
    
    return jsonify({
                "title": event_json["title"],
                "description": event_json["description"],
                "date": event_json["date"],
                "theme": event_json["theme"]
        }), 200

def manage_demo_event(event_id):
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
        'demo/manage.html',
        event=event,
        speakers=speakers,
        participants=participants,
        conferences=conferences,
        visuals=visuals,
        feedbacks=feedbacks,
        page_name='events'
    )

def submit_demo_event():
    try:
        data = request.json
        title = data.get("title")
        date = data.get("date")
        description = data.get("description")

        if not title or not date or not description:
            return jsonify({"success": False, "message": "Tous les champs sont requis."}), 400

        event = Evenement(
            titre=title,
            date=datetime.strptime(date, "%Y-%m-%dT%H:%M"),
            description=description
        )
        db.session.add(event)
        db.session.commit()

        return jsonify({"success": True, "message": "Événement créé avec succès.", "event_id": event.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    

def list_template_events():
    events = Evenement.query.all()
    return render_template('demo/lists.html',page_name='demo', events=events)


def manage_template_event(event_id):
    event = Evenement.query.get_or_404(event_id)
    return render_template('demo/manage.html', page_name='demo', event=event)

def create_template_event_form():
    return render_template('demo/create.html',page_name='demo')

def generate_full_event():
    steps = []
    current_event = Evenement.query.order_by(Evenement.id.desc()).first()




    # 8. Générer des posts pour les réseaux sociaux et visuels associés
    social = generate_social_posts(current_event.id,current_event.titre)
    steps.append({"message": f"{len(social)} posts générés.", "success": True})

    return jsonify({"steps": steps})