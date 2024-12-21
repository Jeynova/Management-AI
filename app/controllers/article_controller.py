from flask import jsonify, request
from app.models import Conference
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_article(conference_id=None, theme=None):
    """Génère un article ou un modèle de post pour une conférence ou un thème donné."""
    try:
        data = request.get_json()
        conference_id = data.get("conference_id")
        theme = data.get("theme")
        if conference_id:
            conference = Conference.query.get(conference_id)
            if not conference:
                return jsonify({"error": "Conférence non trouvée"}), 404

            theme = conference.theme
            speaker = conference.speaker
            bio = speaker.bio if speaker and speaker.bio else "Biographie non spécifiée"

            prompt = f"""
            Tu es un rédacteur professionnel spécialisé en communication événementielle. 
            Rédige un article captivant pour promouvoir une conférence sur le thème suivant :
            - Thème : {theme}
            - Conférencier : {speaker.prenom} {speaker.nom} ({speaker.profession}) si la bio du conférencier est disponible, alors utilise 
            la pour enrichir l'article.
            -Bio conferencier:{bio}

            Structure l'article avec un titre, une introduction engageante, un développement principal et une conclusion invitant à participer.
            """
        elif theme:
            prompt = f"""
            Tu es un rédacteur professionnel spécialisé en communication événementielle. 
            Rédige un article captivant pour promouvoir une conférence sur le thème suivant :
            - Thème : {theme}

            Structure l'article avec un titre, une introduction engageante, un développement principal et une conclusion invitant à participer.
            """
        else:
            return jsonify({"error": "Conférence ou thème requis"}), 400

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un rédacteur expert en communication événementielle."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        article = response.choices[0].message.content.strip()

        return jsonify({"message": "Article généré avec succès", "article": article}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500