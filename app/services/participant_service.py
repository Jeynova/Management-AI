import json
from app.models import Participant
from app import db
import openai
from dotenv import load_dotenv
import os
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_random_participants_with_gpt(batch_size=5, total=10):
    """Génère des participants en lots pour atteindre le total requis."""
    participants = []
    try:
        while len(participants) < total:
            remaining = min(batch_size, total - len(participants))
            prompt = f"""
            Génère {remaining} profils fictifs de participants à une conférence avec les informations suivantes :
            - Nom
            - Prénom
            - Sexe (Homme ou Femme)
            - Âge (entre 18 et 65 ans)
            - Profession
            - Email (format valide)
            Retourne les informations sous forme de JSON (liste de dictionnaires).
            Exemple :
            [
                {{
                    "Nom": "Dupont",
                    "Prenom": "Jean",
                    "Sexe": "Homme",
                    "Age": 30,
                    "Profession": "Data Scientist",
                    "Email": "jean.dupont@email.com"
                }}
            ]
            """
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un générateur de profils professionnels."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            raw_data = response.choices[0].message.content.strip()

            try:
                batch_data = json.loads(raw_data)
                if not isinstance(batch_data, list):
                    raise ValueError(f"Le format attendu est une liste, reçu : {type(batch_data)}")

                # Validation des clés
                required_keys = {"Nom", "Prenom", "Sexe", "Age", "Profession", "Email"}
                for participant in batch_data:
                    missing_keys = required_keys - participant.keys()
                    if missing_keys:
                        raise ValueError(f"Données manquantes : {missing_keys} dans {participant}")

                participants.extend(batch_data)
            except json.JSONDecodeError:
                raise ValueError(f"JSON invalide généré par GPT : {raw_data}")

        return participants[:total]

    except Exception as e:
        raise ValueError(f"Erreur lors de la génération des participants : {str(e)}")

def save_participants_to_db(participants_data):
    """Sauvegarde les participants dans la base de données."""
    participants = []
    for data in participants_data:
        participant = Participant(
            nom=data["Nom"],
            prenom=data["Prenom"],
            sexe=data["Sexe"],
            age=data["Age"],
            profession=data["Profession"],
            email=data["Email"]
        )
        db.session.add(participant)
        participants.append(participant)

    db.session.commit()
    return participants