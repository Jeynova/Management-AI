import os
import json
import requests
from app.models import Visual, db
from flask import jsonify, url_for
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("La clé API OpenAI n'est pas définie dans les variables d'environnement.")
client = OpenAI(api_key=openai_api_key)

IMAGE_FOLDER = os.path.join("app", "static", "images", "visuals")

def save_image_locally(image_content, filename):
    filepath = os.path.join(IMAGE_FOLDER, filename).replace("\\", "/")
    try:
        os.makedirs(IMAGE_FOLDER, exist_ok=True)  # Assurez-vous que le dossier existe
        with open(filepath, "wb") as file:
            file.write(image_content)
        return filepath
    except Exception as e:
        raise ValueError(f"Erreur lors de l'enregistrement de l'image : {str(e)}")

def generate_visual(title, prompt, associated_type=None, associated_id=None,evenement_id=None):
    """
    Génère un visuel via DALL·E et l'enregistre dans la base de données.
    """
    try:
        # Appel à DALL·E
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )
        image_url = response.data[0].url

        # Télécharger l'image générée
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            raise ValueError("Erreur lors du téléchargement de l'image générée.")

        # Enregistrer l'image localement
        image_filename = f"{title.replace(' ', '_')}.png"
        image_path = save_image_locally(image_response.content, image_filename)

        # Enregistrer dans la base de données
        visual = Visual(
            title=title,
            image_url=image_path.split('app/', 1)[-1],
            associated_type=associated_type,
            associated_id=associated_id,
            evenement_id=evenement_id
        )
        db.session.add(visual)
        db.session.commit()

        return {
            "message": "Visuel généré avec succès.",
            "visual": {
                "id": visual.id,
                "title": visual.title,
                "image_url": url_for('static', filename=image_path.split('static/', 1)[-1], _external=True),
                "associated_type": visual.associated_type,
                "associated_id": visual.associated_id,
                "evenement_id": visual.evenement_id
            }
        }
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erreur lors de la génération du visuel : {str(e)}")

def generate_event_visuals(event_id, theme):
    """
    Génère plusieurs visuels cohérents pour un événement spécifique.
    """
    visuals = []
    errors = []
    theme="Nouvelles technologies emergentes"
    # Condenser le thème si nécessaire
    condensed_theme = theme[:100] + "..." if len(theme) > 100 else theme

    # Style unifié pour les visuels
    style_guideline = "Design moderne, minimaliste, et professionnel avec une palette de couleurs technologiquement innovante."

    prompts = [
        {
            "title": "Logo de l'événement",
            "prompt": f"Vous êtes un expert en design graphique et marketing digital.Avec un souçis d'excellence et de haute qualité,créez un logo pour un événement technologique intitulé '{condensed_theme}'.Tes creations sont toujours le plus qualitatif possible mais aussi creative.Tu ne recherches et fais que l'excellence en remettant toujours ton travail en question. "
                      f"Le logo doit refléter {style_guideline} et être reconnaissable immédiatement.",
        },
        {
            "title": "Affiche de la conférence",
            "prompt": f"Vous êtes un expert en design graphique et marketing digital.Avec un souçis d'excellence et de haute qualité,créez une affiche visuellement captivante pour une conférence intitulée '{condensed_theme}'.Tes creations sont toujours le plus qualitatif possible mais aussi creative.Tu ne recherches et fais que l'excellence en remettant toujours ton travail en question. "
                      f"L'affiche doit inclure des éléments futuristes et refléter {style_guideline}.",
        },
        {
            "title": "Bannière web",
            "prompt": f"Créez une bannière web professionnelle pour un événement intitulé '{condensed_theme}'.Tes creations sont toujours le plus qualitatif possible mais aussi creative.Tu ne recherches et fais que l'excellence en remettant toujours ton travail en question. "
                      f"La bannière doit être adaptée aux sites web et refléter {style_guideline}.",
        }
    ]

    for visual in prompts:
        try:
            print(f"Début de la génération : {visual['title']}")  # Debug
            result = generate_visual(
                title=visual["title"],
                prompt=visual["prompt"],
                associated_type="event",
                associated_id=event_id,
                evenement_id=event_id
            )
            visuals.append(result)
            print(f"{visual['title']} généré avec succès.")
        except Exception as e:
            print(f"Erreur lors de la génération de {visual['title']} : {e}")
            errors.append(f"{visual['title']} : {e}")

    return {
        "message": f"{len(visuals)} visuels générés avec succès. {len(errors)} erreurs.",
        "visuals": visuals,
        "errors": errors
    }