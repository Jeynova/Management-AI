from sqlalchemy.event import listen
from sqlalchemy.orm import sessionmaker
import requests
import os

from app.models import FileAnswer

# Function to send data to Pipedream after an insert
def after_insert_listener(mapper, connection, target):
    try:
        print(f"Listener déclenché pour {target.filename}")  # Log simple pour vérifier le déclenchement

        # Construction du payload
        pipedream_url = os.getenv("PIPEDREAM_SQL")
        if not pipedream_url:
            print("URL Pipedream introuvable dans les variables d'environnement")
            return

        payload = {
            "filename": target.filename,
            "response": target.response,
            "event_id": target.evenement_id,
        }

        # Envoi des données à Pipedream
        print(f"Payload envoyé : {payload}")
        response = requests.post(pipedream_url, json=payload)
        print(f"Statut de la réponse : {response.status_code}")
        print(f"Contenu de la réponse : {response.text}")
        print(f"Requête envoyée : {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Erreur lors de l'envoi à Pipedream : {str(e)}")
        print(f"Erreur lors de l'envoi à Pipedream : {str(e)}")
        
listen(FileAnswer, "after_insert", after_insert_listener)
