import json
from app.models import Article, Conference, Evenement
from app import db
import openai
from flask import flash, jsonify, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_single_article(conference=None, event=None, article_type="blog"):
    """
    Génère un article unique pour une conférence ou un événement donné.
    :param conference: Objet Conference, si l'article est pour une conférence.
    :param event: Objet Evenement, si l'article est pour un événement.
    :param article_type: Type d'article à générer ("blog", "scientific_review", etc.).
    """
    if not conference and not event:
        raise ValueError("Une conférence ou un événement est requis pour générer un article.")

    # Définir le prompt pour GPT
    if conference:
        prompt = f"""
        Rédige un article de type {article_type} pour la conférence suivante :
        - Thème : {conference.theme}
        - Conférencier : {conference.speaker.prenom} {conference.speaker.nom} ({conference.speaker.profession})
        {f"- Biographie du conférencier : {conference.speaker.bio}" if conference.speaker.bio else ""}
        """
    elif event:
        prompt = f"""
        Rédige un article de type {article_type} pour promouvoir l'événement suivant :
        - Titre : {event.titre}
        - Date : {event.date.strftime('%Y-%m-%d')}
        - Description : {event.description or "Pas de description fournie."}
        """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un rédacteur expert en communication événementielle."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        raw_response = response.choices[0].message.content.strip()
    except Exception as e:
        raise ValueError(f"Erreur lors de la génération de l'article : {str(e)}")

    try:
        # Parse JSON et validation
        article_json = json.loads(raw_response)
        title = article_json["title"]
        content = article_json["content"]

        return Article(
            title=title,
            content=content,
            type=article_type,
            evenement_id=event.id if event else None,
            conference_id=conference.id if conference else None
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide généré par GPT : {str(e)}")
    
def generate_articles_for_event(event_id):
    """Génère des articles variés pour un événement et ses conférences."""
    try:
        # Récupérer l'événement
        event = Evenement.query.get(event_id)
        if not event:
            return {"message": "Événement non trouvé.", "success": False}

        articles = []

        # Article de blog pour l'événement
        try:
            event_blog_article = generate_single_article(event=event, article_type="blog")
            db.session.add(event_blog_article)
            articles.append(event_blog_article)
        except Exception as e:
            print(f"Erreur lors de la génération de l'article de blog pour l'événement : {e}")

        # Article scientifique pour l'événement
        try:
            event_scientific_article = generate_single_article(event=event, article_type="scientific_review")
            db.session.add(event_scientific_article)
            articles.append(event_scientific_article)
        except Exception as e:
            print(f"Erreur lors de la génération de l'article scientifique pour l'événement : {e}")

        # Articles pour les conférences
        conferences = Conference.query.filter_by(evenement_id=event_id).all()
        for conference in conferences:
            for article_type in ["blog", "scientific_review", random.choice(["announcement", "recap", "interview"])]:
                try:
                    conference_article = generate_single_article(conference=conference, article_type=article_type)
                    db.session.add(conference_article)
                    articles.append(conference_article)
                except Exception as e:
                    print(f"Erreur lors de la génération de l'article {article_type} pour la conférence {conference.id} : {e}")

        # Commit des articles générés
        db.session.commit()

        return {
            "message": f"{len(articles)} articles générés avec succès.",
            "articles": [
                {
                    "title": article.title,
                    "type": article.type,
                    "conference": article.conference.theme if article.conference else None,
                    "event": article.evenement_id
                } for article in articles
            ],
            "success": True
        }

    except Exception as e:
        db.session.rollback()
        return {"message": f"Erreur lors de la génération des articles : {e}", "success": False}
    
def generate_article_logic(event_id=None, conference_id=None):
    """Génère un article en fonction de l'événement ou de la conférence."""
    print(f"Début de génération d'article : event_id={event_id}, conference_id={conference_id}")
    prompt = None  # Initialiser le prompt par défaut
    if event_id:
        event = Evenement.query.get(event_id)
    
    if conference_id:
        conference = Conference.query.get(conference_id)
        print(f"Conférence récupérée : {conference}")
        if not conference:
            raise ValueError("Conférence non trouvée.")

        speaker = conference.speaker
        if speaker and speaker.bio:
            # Article pour une conférence avec un conférencier et une biographie
            prompt = f"""
            Tu es un rédacteur spécialisé en communication événementielle.
            Je veux que tu génères un JSON structuré pour un article, sans texte additionnel en dehors du JSON. 
            Assure-toi que les chaînes de caractères soient correctement échappées. Voici les champs que je veux:
                - `title` : un titre captivant et court.
                - `type` : le type d'article (par exemple, "marketing", "annonce", "recap").
                - `content` : Rédige un article captivant pour promouvoir une conférence sur le thème suivant Structure l'article avec un titre, une introduction engageante, un développement  principal détaillant le sujet et le conférencier, et une conclusion invitant à participer :
                                - Thème : {conference.theme}
                                - Conférencier : {speaker.prenom} {speaker.nom} ({speaker.profession})
                                - Biographie du conférencier : {speaker.bio}

            Le JSON doit suivre ce format et ne contenir que le JSON:
            {{
                "title": "Titre généré",
                "type": "Type d'article",
                "content": "Texte complet de l'article"
            }}
            Tu dois retourner un JSON FORMATTE CLAIR ET UTILISABLE.
            """
        else:
            # Article pour une conférence sans biographie de conférencier
            prompt = f"""
            Tu es un rédacteur spécialisé en communication événementielle.
            Je veux que tu génères un JSON structuré pour un article, sans texte additionnel en dehors du JSON. 
            Assure-toi que les chaînes de caractères soient correctement échappées. Voici les champs que je veux:
                - `title` : un titre captivant et court.
                - `type` : le type d'article (par exemple, "marketing", "annonce", "recap").
                - `content` : Rédige un article captivant pour promouvoir une conférence sur le thème suivant :
                - Thème : {conference.theme}. Structure l'article avec un titre, une introduction engageante, un développement principal détaillant le sujet et ses bénéfices, et une   conclusion invitant à participer.

            Le JSON doit suivre ce format:
            {{
                "title": "Titre généré",
                "type": "Type d'article",
                "content": "Texte complet de l'article"
            }}
            Tu dois retourner un JSON FORMATTE CLAIR ET UTILISABLE.
            """
    elif event_id:
        
        print(f"Événement récupéré : {event}")
        if not event:
            raise ValueError("Événement non trouvé.")

        # Article général sur l'événement
        prompt = f"""
        Tu es un rédacteur spécialisé en communication événementielle.
        Je veux que tu génères un JSON structuré pour un article, sans texte additionnel en dehors du JSON. 
        Assure-toi que les chaînes de caractères soient correctement échappées. Voici les champs que je veux:
        - `title` : un titre captivant et court.
        - `type` : le type d'article (par exemple, "marketing", "annonce", "recap").
        - `content` :Rédige un article captivant pour promouvoir un événement intitulé "{event.titre}".
        - Date : {event.date.strftime('%Y-%m-%d')}
        - Description : {event.description or "Pas de description fournie."}

        Structure l'article avec un titre, une introduction engageante, un développement principal
        Le JSON doit suivre ce format:
        {{
            "title": "Titre généré",
            "type": "Type d'article",
            "content": "Texte complet de l'article"
        }}
        détaillant les points forts de l'événement, et une conclusion invitant à y participer.
        Tu dois retourner un JSON FORMATTE CLAIR ET UTILISABLE.
        """
    else:
        # Si aucun ID n'est fourni, lever une exception
        raise ValueError("Un ID d'événement ou de conférence est requis pour générer un article.")

    # Génération de l'article via GPT
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un rédacteur expert en communication événementielle."},
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
        article_json = json.loads(raw_response)

        # Extract required fields
        title = article_json["title"]
        article_type = article_json["type"]
        content = article_json["content"]
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur lors de l'analyse du JSON généré par GPT : {str(e)}")
    except KeyError as e:
        raise ValueError(f"Erreur : Clé manquante dans la réponse JSON : {str(e)}")

    # Return an Article object
    return Article(
        title=title,
        content=content,
        type=article_type,
        evenement_id=event_id if event_id else None,
        conference_id=conference_id if conference_id else None
    )

def create_article():
    """Crée un nouvel article."""
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        conference_id = request.form.get('conference_id')

        try:
            article = generate_article_logic(event_id=event_id, conference_id=conference_id)
            db.session.add(article)
            db.session.commit()
            flash("Article généré avec succès.", "success")
        except Exception as e:
            flash(f"Erreur lors de la génération de l'article : {e}", "danger")

        return redirect(url_for('list_articles'))

    events = Evenement.query.all()
    conferences = Conference.query.all()
    return render_template('articles/create.html', events=events, conferences=conferences)


def create_article_api():
    """Crée un nouvel article via API."""
    data = request.get_json()  # Récupère les données JSON
    event_id = data.get("event_id")
    conference_id = data.get("conference_id")

    try:
        # Générer l'article
        article = generate_article_logic(event_id=event_id, conference_id=conference_id)
        print(f"Article dans api : {article}")
        db.session.add(article)
        db.session.commit()
        conference_theme = article.conference.theme if article.conference else "Non liée à une conférence"

        return jsonify({
            "message": "Article créé avec succès.",
            "article": {
                "title": article.title,
                "content": article.content,
                "conference": conference_theme
            }
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la création de l'article : {str(e)}"}), 500
