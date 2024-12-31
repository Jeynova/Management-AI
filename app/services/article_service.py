import json
from app.models import Article, Conference, Evenement, Participant, Speaker
from app import db
import openai
from flask import flash, jsonify, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta
import re

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_gpt_response_to_article(raw_response):
    """
    Parse une réponse textuelle structurée en un dictionnaire.
    """
    try:
        # Extraire les champs à partir du texte structuré
        lines = raw_response.split("\n")
        title = next((line.split(":")[1].strip() for line in lines if line.startswith("Titre:")), None)
        article_type = next((line.split(":")[1].strip() for line in lines if line.startswith("Type:")), None)
        content_index = next((i for i, line in enumerate(lines) if line.startswith("Contenu:")), None)
        
        if not (title and article_type and content_index is not None):
            raise ValueError("Champs obligatoires manquants dans la réponse GPT.")

        # Le contenu commence après la ligne "Contenu:"
        content = "\n".join(lines[content_index + 1:]).strip()

        return {
            "title": title,
            "type": article_type,
            "content": content
        }
    except Exception as e:
        raise ValueError(f"Erreur lors du parsing de la réponse GPT : {str(e)}\nRéponse brute : {raw_response}")
    
def generate_single_article(conference=None, event=None, article_type="blog", target_audience=None):
    """
    Génère un article unique pour une conférence ou un événement donné.
    Prend en charge les communiqués de presse avec un public cible.
    """
    if not conference and not event:
        raise ValueError("Une conférence ou un événement est requis pour générer un article.")

    # Construire le prompt
    if conference:
        event= Evenement.query.get(conference.evenement_id)
        prompt = f"""
        Rédige un article de type '{article_type}' pour la conférence suivante :
        - Thème : {conference.theme}
        - Conférencier : {conference.speaker.prenom} {conference.speaker.nom} ({conference.speaker.profession})
        {f"- Biographie du conférencier : {conference.speaker.bio}" if conference.speaker.bio else ""}
        Adapte le style, la longueur de l'article et le public cible en fonction du type de conférence et du tupe d'article.
        Retourne le contenu sous le format suivant :
        Titre: [Titre de l'article]
        Type: [Type de l'article]
        Contenu:
        [Contenu détaillé et engageant de l'article]
        """
    elif event:
        prompt = f"""
        Rédige un article de type '{article_type}' pour promouvoir l'événement suivant :
        - Titre : {event.titre}
        - Date : {event.date.strftime('%Y-%m-%d')}
        - Description : {event.description or "Pas de description fournie."}
        {f"- Cible : {target_audience}" if target_audience else ""}
        Adapte le style, la longueur de l'article et le public cible en fonction du type de conférence et du tupe d'article.
        Retourne le contenu sous le format suivant :
        Titre: [Titre de l'article]
        Type: [Type de l'article]
        Contenu:
        [Contenu détaillé et engageant de l'article]
        """

    try:
        # Appel à GPT
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un expert en rédaction de contenu événementiel."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        raw_response = response.choices[0].message.content.strip()
        # Parse la réponse textuelle
        article_data = parse_gpt_response_to_article(raw_response)

        return Article(
            title=article_data["title"],
            content=article_data["content"],
            type=article_data["type"],
            evenement_id=event.id if event else None,
            conference_id=conference.id if conference else None
        )
    except Exception as e:
        raise ValueError(f"Erreur lors de la génération de l'article : {str(e)}")


def generate_articles(event_id, num_articles=1):
    """
    Génère plusieurs articles pour un événement et ses conférences.
    """
    try:
        # Récupérer l'événement
        event = Evenement.query.get(event_id)
        if not event:
            raise ValueError("Événement non trouvé.")

        # Récupérer les conférences associées
        conferences = Conference.query.filter_by(evenement_id=event_id).all()

        # Types d'articles disponibles
        article_types = ["blog", "scientific_review", "announcement", "recap", "interview"]
        target_audiences = ["presse écrite", "journaux spécialisés", "réseaux sociaux", "newsletters","Post twitter"]

        articles = []

        for _ in range(num_articles):
            # Randomiser la cible (événement ou conférence)
            target = "conference" if conferences and random.choice([True, False]) else "event"
            article_type = random.choice(article_types)
            target_audience = random.choice(target_audiences) if article_type == "announcement" else None

            # Générer l'article
            try:
                if target == "conference":
                    conference = random.choice(conferences)
                    article = generate_single_article(conference=conference, article_type=article_type)
                else:
                    article = generate_single_article(event=event, article_type=article_type, target_audience=target_audience)

                db.session.add(article)
                articles.append(article)
            except Exception as e:
                print(f"Erreur lors de la génération de l'article {article_type} pour la cible {target} : {e}")

        # Commit des articles
        db.session.commit()

        return {
            "message": f"{len(articles)} articles générés avec succès.",
            "articles": [
                {
                    "title": article.title,
                    "type": article.type,
                    "conference": article.conference.theme if article.conference else None,
                    "event": event_id
                } for article in articles
            ],
            "success": True
        }

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la génération des articles : {str(e)}"}), 500
    
def create_mock_data():
    """Crée un jeu de données simulé pour tester les articles et feedbacks."""
    try:
        # Supprimer les données existantes
        db.session.query(Article).delete()
        db.session.query(Conference).delete()
        db.session.query(Participant).delete()
        db.session.query(Evenement).delete()

        # Ajouter un événement simulé
        event = Evenement(
            titre="Tech Titans 2025",
            date=datetime(2025, 2, 27),
            description="Un événement majeur pour explorer les tendances technologiques de demain."
        )
        db.session.add(event)
        db.session.flush()

        # Ajouter des participants simulés
        participants = []
        for i in range(10):
            participant = Participant(
                email=f"participant{i}@example.com",
                nom=f"Nom{i}",
                prenom=f"Prénom{i}",
                sexe="Homme" if i % 2 == 0 else "Femme",
                age=random.randint(18, 60),
                profession="Profession simulée"
            )
            db.session.add(participant)
            participants.append(participant)

        # Ajouter des conférenciers et conférences simulés
        speakers = []
        conferences = []
        for i in range(3):
            speaker = Speaker(
                nom=f"Conférencier{i}",
                prenom=f"PrénomConférencier{i}",
                age=random.randint(30, 60),
                sexe="Homme" if i % 2 == 0 else "Femme",
                profession="Expert en IA",
                bio=f"Biographie de Conférencier{i}, expert en technologies et IA."
            )
            db.session.add(speaker)
            speakers.append(speaker)
            db.session.flush()

            conference = Conference(
                theme=f"Thème de conférence {i}",
                speaker_id=speaker.id,
                horaire=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                description=f"Description de la conférence {i}.",
                evenement_id=event.id
            )
            db.session.add(conference)
            conferences.append(conference)

        db.session.commit()
        return {"event": event, "participants": participants, "conferences": conferences}
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erreur lors de la création des données simulées : {str(e)}")
    
def test_articles():
    """Route pour tester la génération d'articles sur des données simulées."""
    try:
        mock_data = create_mock_data()
        event = mock_data["event"]
        response = generate_articles(event.id, num_articles=5)  # Génère 5 articles
        return response
    except Exception as e:
        return jsonify({"error": f"Erreur lors du test des articles : {str(e)}"}), 500
    
def generate_press_releases(event, media_types=["presse écrite", "journaux spécialisés", "réseaux sociaux", "newsletters"]):
    """
    Génère des communiqués de presse pour différents médias et retourne les résultats.
    """
    releases = []
    for media in media_types:
        prompt = f"""
        Rédige un communiqué de presse pour promouvoir l'événement suivant :
        - Titre : {event.titre}
        - Date : {event.date.strftime('%Y-%m-%d')}
        - Description : {event.description or "Pas de description fournie."}
        Médium : {media}
        Style : Adapté à {media}.
        Format attendu :
        Titre: [Titre du communiqué]
        Contenu:
        [Texte du communiqué]
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un expert en rédaction de communiqués de presse."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            content = response.choices[0].message.content.strip()
            releases.append({
                "media": media,
                "content": content
            })
        except Exception as e:
            print(f"Erreur lors de la génération pour {media} : {e}")

    return {
        "message": f"{len(releases)} communiqués générés.",
        "releases": releases,
        "success": len(releases) > 0
    }