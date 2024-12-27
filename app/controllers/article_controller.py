from flask import jsonify, request, render_template, redirect, url_for, flash
from app.models import Conference, Evenement, Article, db
import openai
import os
from dotenv import load_dotenv
import pandas as pd
import json
import re

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def manage_articles(event_id):
    """Gère les articles liés à un événement."""
    event = Evenement.query.get_or_404(event_id)
    conferences = Conference.query.filter_by(evenement_id=event_id).all()
    articles = Article.query.filter_by(evenement_id=event_id).all()

    return render_template('articles/manage.html', event=event, conferences=conferences, articles=articles,page_name='articles')

def clean_json_response(raw_response):
    """Nettoie et extrait le JSON d'une réponse brute."""
    # Supprimer les caractères indésirables avant de parser
    try:
        # Rechercher un bloc JSON dans la réponse
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            cleaned_response = match.group(0)
            # Remplacer les retours à la ligne non échappés par des espaces
            cleaned_response = re.sub(r'(?<!\\)\n', ' ', cleaned_response)
            # Remplacer les guillemets non échappés
            cleaned_response = re.sub(r'(?<!\\)"', r'\"', cleaned_response)
            return cleaned_response
        else:
            raise ValueError("Aucun JSON valide trouvé dans la réponse.")
    except Exception as e:
        raise ValueError(f"Erreur lors du nettoyage de la réponse : {str(e)}")

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

def generate_articles_from_sponsor_file(file_path):
    """Génère des articles basés sur les données des sponsors fournies dans un fichier."""
    # Charger les données du fichier sponsors
    try:
        sponsors_df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du fichier : {e}")

    articles = []
    for _, sponsor in sponsors_df.iterrows():
        # Construire le prompt pour chaque sponsor
        prompt = f"""
        Vous êtes un rédacteur spécialisé en communication événementielle.
        Rédigez un article captivant pour mettre en avant un sponsor de notre événement :
        - Nom du Sponsor : {sponsor['Nom_Sponsor']}
        - Niveau de Sponsoring : {sponsor['Niveau_Sponsoring']}
        - Montant Investi : {sponsor['Montant_Investi']} €
        - Visibilité Offerte : {sponsor['Visibilite_Offerte']}
        - Engagement sur les Réseaux Sociaux : {sponsor['Engagement_Reseaux_Sociaux']} mentions
        - Leads Générés : {sponsor['Leads_Generes']}

        Structurez l'article avec un titre, une introduction engageante, un développement principal 
        détaillant les avantages offerts au sponsor et son impact, et une conclusion encourageant
        d'autres entreprises à sponsoriser nos événements futurs.
        """

        try:
            # Appel à l'API GPT pour générer l'article
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un rédacteur expert en communication événementielle."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            content = response.choices[0].message.content.strip()

            # Créer un article pour le sponsor
            articles.append(Article(
                title=f"Focus Sponsor : {sponsor['Nom_Sponsor']}",
                content=content,
                event_id=None  # Aucun événement ou conférence spécifique lié ici
            ))

        except openai.error.OpenAIError as e:
            flash(f"Erreur GPT pour le sponsor {sponsor['Nom_Sponsor']} : {e}", "danger")
            continue

    return articles

def generate_articles_from_sponsor_file(file):
    """Génère des articles à partir des données sponsors d'un fichier."""
    try:
        # Lire les données depuis le fichier CSV
        sponsors_df = pd.read_csv(file)

        articles = []
        for _, sponsor in sponsors_df.iterrows():
            prompt = f"""
            Vous êtes un rédacteur spécialisé en communication événementielle.
            Rédigez un article captivant pour mettre en avant un sponsor de notre événement :
            - Nom du Sponsor : {sponsor['Nom_Sponsor']}
            - Niveau de Sponsoring : {sponsor['Niveau_Sponsoring']}
            - Montant Investi : {sponsor['Montant_Investi']} €
            - Visibilité Offerte : {sponsor['Visibilite_Offerte']}
            - Engagement sur les Réseaux Sociaux : {sponsor['Engagement_Reseaux_Sociaux']} mentions
            - Leads Générés : {sponsor['Leads_Generes']}

            Structurez l'article avec un titre, une introduction engageante, un développement principal 
            détaillant les avantages offerts au sponsor et son impact, et une conclusion encourageant
            d'autres entreprises à sponsoriser nos événements futurs.
            """

            try:
                # Appel à l'API GPT
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Veuillez assumer le rôle d'un expert en communication événementielle. Votre tâche est de créer des articles professionnels et complets liés à des événements ou conférences. Cette tâche spécifique implique la rédaction d'un article basé sur un fichier d'importation de sponsors d'événement."

                        # Directives

                            "- **Adopter un ton professionnel** : Assurez-vous que l'article reste professionnel tout en étant engageant et informatif."
                            "- **Détailler les hypothèses** : Si des hypothèses sont nécessaires pour le contenu de l'article, expliquez-les clairement."
                            "- **Organiser le contenu** : Utilisez des sections ou des puces pour clarifier les points clés et améliorer la lisibilité."

                            # Développement de l'article

                            "- Soyez minutieux dans l'identification des détails pertinents des sponsors et comment ils contribuent au succès de l'événement."
                            "- Fournir des explications approfondies soutenues par des données sur les sponsors."
                            "- Assurez-vous que vos conclusions et informations apportent une réelle valeur ajoutée à l'article."

                            # Recommandations

                            "- Offrir des insights basés sur l'analyse des sponsors, et expliquer comment ils peuvent être intégrés dans l'article."
                            "- Garder les intérêts du public à l'esprit pour offrir un contenu pertinent et engageant."

                            # Format de sortie

                            "Répondez sous forme de sections structurées ou de listes numérotées pour chaque point clé. Pour des explications complexes, fournissez des paragraphes concis suivis d'informations exploitables."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000
                )
                content = response.choices[0].message.content.strip()

                # Ajouter l'article à la liste
                articles.append(Article(
                    title=f"Focus Sponsor : {sponsor['Nom_Sponsor']}",
                    content=content,
                    event_id=None  # Pas de lien direct avec un événement
                ))

            except openai.error.OpenAIError as e:
                flash(f"Erreur GPT pour le sponsor {sponsor['Nom_Sponsor']} : {e}", "danger")
                continue

        return articles
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement ou du traitement du fichier : {e}")


def create_articles_from_file():
    """API pour créer des articles depuis un fichier sponsors."""
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Nom de fichier invalide."}), 400

    try:
        articles = generate_articles_from_sponsor_file(file)
        for article in articles:
            db.session.add(article)
        db.session.commit()

        return jsonify({"message": f"{len(articles)} articles générés avec succès."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

