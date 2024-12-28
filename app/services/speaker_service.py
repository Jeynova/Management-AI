import json
from app.models import Speaker
from app import db
import openai
from dotenv import load_dotenv
import os
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_random_speakers_with_biographies(batch_size=2, total=5):
    """Génère des orateurs avec biographies."""
    speakers = []
    try:
        while len(speakers) < total:
            remaining = min(batch_size, total - len(speakers))
            prompt = f"""
            Génère {remaining} profils fictifs d'orateurs pour une conférence avec les informations suivantes :
            - Nom
            - Prénom
            - Sexe (Homme ou Femme)
            - Âge (entre 25 et 65 ans)
            - Profession
            - Une biographie captivante décrivant leurs réalisations et expertise professionnelle
            Retourne les informations sous forme de JSON (liste de dictionnaires).
            Assure-toi que toutes les clés respectent exactement cette orthographe et ce format.
            Exemple :
            [
                {{
                    "Nom": "Dupont",
                    "Prenom": "Jean",
                    "Sexe": "Homme",
                    "Age": 45,
                    "Profession": "Expert en cybersécurité",
                    "Bio": "Jean Dupont est un expert renommé en cybersécurité avec 20 ans d'expérience..."
                }}
            ]
            """
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un générateur de profils d'orateurs professionnels."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            raw_data = response.choices[0].message.content.strip()
            

            try:
                batch_data = json.loads(raw_data)
                if not isinstance(batch_data, list):
                    raise ValueError(f"Le format attendu est une liste, reçu : {type(batch_data)}")

                # Validation des clés pour chaque orateur
                required_keys = {"Nom", "Prenom", "Sexe", "Age", "Profession", "Bio"}
                for speaker in batch_data:
                    missing_keys = required_keys - speaker.keys()
                    if missing_keys:
                        raise ValueError(f"Données manquantes : {missing_keys} dans {speaker}")

                speakers.extend(batch_data)
            except json.JSONDecodeError:
                raise ValueError(f"JSON invalide généré par GPT : {raw_data}")

        return speakers[:total]

    except Exception as e:
        raise ValueError(f"Erreur lors de la génération des orateurs : {str(e)}")
    

def save_speakers_with_biographies_to_db(speakers_data):
    """Sauvegarde les orateurs et leurs biographies dans la base de données."""
    speakers = []
    try:
        for data in speakers_data:
            # Vérifiez que toutes les clés sont présentes
            if not all(key in data for key in ["Nom", "Prenom", "Sexe", "Age", "Profession", "Bio"]):
                raise ValueError(f"Données incomplètes pour l'orateur : {data}")

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