import random
import json
from datetime import datetime
from app.models import SocialPost, db
from app.services.visual_service import generate_visual
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_social_posts(event_id, theme, number_of_posts=2):
    """
    Génère des publications pour les réseaux sociaux avec images.
    - Génère `number_of_posts` publications pour Facebook, Instagram et X.
    - Chaque publication contient du contenu et une image correspondante.

    :param event_id: ID de l'événement associé
    :param theme: Thème de l'événement
    :param number_of_posts: Nombre total de publications à générer
    :return: Un dictionnaire avec les résultats
    """
    platforms = ["Facebook", "Instagram", "X"]
    posts = []
    
    try:
        for _ in range(number_of_posts):
            # Sélectionner une plateforme aléatoire
            platform = random.choice(platforms)
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
            # Générer le contenu de la publication via ChatGPT
            prompt = f"""
            Vous êtes un expert Social media manager et vos creations sont toujours excellente et creative.Tu ne recherches que l'excellence en remettant toujours ton travail en question avant un post. Génère une publication pour {platform} pour promouvoir un événement intitulé '{theme}' :
            - La publication doit être concise et engageante.
            - Utilise un style adapté à {platform}.
            - Inclut un appel à l'action (CTA) adapté.
            Retourne uniquement le texte sous forme de JSON :
            {{
                "content": "Texte de la publication."
            }}
            """
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un expert en rédaction de contenu pour les réseaux sociaux."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            raw_response = response.choices[0].message.content.strip()
            content_json = json.loads(raw_response)
            date=datetime.now()
            # Générer une image correspondante via DALL·E
            prompt_details = f"Vous êtes un expert en graphic design.En tant que lead designer et responable marketing digital, Créez une image visuellement attrayante et creative pour une publication sur {platform} relative à '{theme}'. " \
                             "Assurez-vous que l'image reflète le thème technologique et soit adaptée au format de {platform}."
            visual = generate_visual(
                title=f"Visuel {timestamp_str} {platform}",
                prompt=prompt_details,
                associated_type="social_post",
                associated_id=None,  # L'association sera faite après la création du post
                evenement_id=event_id
            )

            # Créer l'objet SocialPost
            social_post = SocialPost(
                platform=platform,
                content=content_json["content"],
                image_url=visual.get("image_url"),  # Récupérer l'URL de l'image générée
                evenement_id=event_id
            )
            db.session.add(social_post)
            posts.append(social_post)

        # Sauvegarder tous les posts générés
        db.session.commit()

        return {
            "message": f"{len(posts)} publications générées avec succès pour les réseaux sociaux.",
            "posts": [
                {
                    "platform": post.platform,
                    "content": post.content,
                    "image_url": post.image_url
                } for post in posts
            ]
        }

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erreur lors de la génération des publications pour les réseaux sociaux : {str(e)}")