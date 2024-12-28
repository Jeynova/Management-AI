import json
from app.models import Participant
from app import db
import openai
from dotenv import load_dotenv
import os
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_random_participants_with_gpt(number):
    """Génère plusieurs participants fictifs via GPT."""
    prompt = f"""
    Génère {number} profils fictifs de participants à une conférence avec les informations suivantes :
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
            "Age": 40,
            "Profession": "Ingénieur en informatique",
            "Email": "jean.dupont@email.com"
        }},
        {{
            "Nom": "Martin",
            "Prenom": "Marie",
            "Sexe": "Femme",
            "Age": 30,
            "Profession": "Designer UX",
            "Email": "marie.martin@email.com"
        }}
    ]
    """

    # Appeler GPT
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un générateur de données fictives."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    raw_data = response.choices[0].message.content.strip()

    # Parse JSON
    try:
        participants_data = json.loads(raw_data)
        if not isinstance(participants_data, list):
            raise ValueError("Le format attendu est une liste de dictionnaires.")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide généré par GPT : {str(e)}")

    return participants_data

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