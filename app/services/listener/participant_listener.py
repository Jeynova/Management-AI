from sqlalchemy.event import listen
from sqlalchemy.orm import mapper
import requests
import base64
import qrcode
from io import BytesIO
from app.models import Participant

def after_insert_listener(mapper, connection, target):
    """
    Listener SQLAlchemy déclenché après l'insertion d'un participant.
    """
    try:
        print(f"Nouvel enregistrement détecté : {target.nom} {target.prenom}")

        # Générer le QR Code
        qr_data = f"Participant: {target.prenom} {target.nom}, Email: {target.email}, ID: {target.id}"
        qr = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr.save(qr_buffer)
        qr_buffer.seek(0)

        # Encode QR code image en base64
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

        # Préparer les données pour le webhook
        payload = {
            "nom": target.nom,
            "prenom": target.prenom,
            "email": target.email,
            "age": target.age,
            "qr_code": qr_base64
        }

        # URL du webhook Pipedream
        pipedream_url = "https://eou1r9maglcv9jv.m.pipedream.net"

        # Envoyer au webhook
        response = requests.post(pipedream_url, json=payload)
        if response.status_code == 200:
            print("Webhook déclenché avec succès.")
        else:
            print(f"Erreur lors de l'envoi au webhook : {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Erreur dans le listener after_insert : {str(e)}")

# Attacher le listener à la table Participant
listen(Participant, "after_insert", after_insert_listener)