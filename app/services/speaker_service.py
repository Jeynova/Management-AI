import json
from app.models import Speaker
from app import db
import openai
from dotenv import load_dotenv
import os
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_random_speakers_with_biographies(number=5):
    """Génère plusieurs orateurs avec biographies via GPT."""
    try:
        # Prompt pour GPT
        prompt = f"""
        Génère {number} profils fictifs d'orateurs à une conférence. Pour chaque orateur, inclure :
        - Nom
        - Prénom
        - Sexe (Homme ou Femme)
        - Âge (entre 25 et 65 ans)
        - Profession (spécialisée dans un domaine technique ou académique mais en rapport avec les nouvelles technologies)
        - Une biographie captivante décrivant leurs réalisations et expertise professionnelle basé sur les informations du speaker.Cette bio servira probablement pour la creation de conference et/ou article et doit donc être complete,precise,professionnelle et captivante..
        Retourne les informations sous forme de JSON (liste de dictionnaires).
        Exemple :
        [
            {{
                "Nom": "Dupont",
                "Prenom": "Jean",
                "Sexe": "Homme",
                "Age": 45,
                "Profession": "Expert en cybersécurité",
                "Bio": "Jean Dupont est un expert renommé en cybersécurité avec plus de 20 ans d'expérience..."
            }},
            {{
                "Nom": "Martin",
                "Prenom": "Marie",
                "Sexe": "Femme",
                "Age": 38,
                "Profession": "Chercheuse en intelligence artificielle",
                "Bio": "Marie Martin est une chercheuse pionnière dans le domaine de l'intelligence artificielle..."
            }}
        ]
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un générateur de profils professionnels complets."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000  # Augmenté pour permettre une réponse plus grande
        )

        raw_data = response.choices[0].message.content.strip()

        # Parse JSON et validation
        try:
            speakers_data = json.loads(raw_data)
            if not isinstance(speakers_data, list):
                raise ValueError("Le format attendu est une liste de dictionnaires.")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide généré par GPT : {str(e)}")

        return speakers_data

    except Exception as e:
        raise ValueError(f"Erreur lors de la génération des orateurs et biographies : {str(e)}")

def save_speakers_with_biographies_to_db(speakers_data):
    """Sauvegarde les orateurs et leurs biographies dans la base de données."""
    try:
        speakers = []
        for data in speakers_data:
            speaker = Speaker(
                nom=data["Nom"],
                prenom=data["Prenom"],
                sexe=data["Sexe"],
                age=data["Age"],
                profession=data["Profession"],
                bio=data["Bio"]
            )
            db.session.add(speaker)
            speakers.append(speaker)

        db.session.commit()
        return speakers

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erreur lors de la sauvegarde des orateurs : {str(e)}")
    
def generate_speakers_with_biographies(number=5):
    """Génère et sauvegarde plusieurs orateurs avec biographies."""
    try:
        # Étape 1 : Générer les orateurs et biographies
        speakers_data = generate_random_speakers_with_biographies(number)

        # Étape 2 : Sauvegarder dans la base
        speakers = save_speakers_with_biographies_to_db(speakers_data)

        return speakers

    except Exception as e:
        raise ValueError(f"Erreur lors de la génération et sauvegarde des orateurs : {str(e)}")