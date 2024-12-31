from flask import render_template, request, redirect, url_for, flash, jsonify
import requests
from app.models import Participant, db
import openai
import random
import json
from flask_mail import Message
from io import BytesIO
import qrcode
from app.models import Participant
import os
from app import db
import sys
from mailtrap import Address, Mail, MailtrapClient
import base64

def manage_participants(event_id):
    """Gère les participants."""
    if request.method == 'POST':
        # Ajouter un participant
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        sexe = request.form.get('sexe')
        age = request.form.get('age')
        profession = request.form.get('profession')

        try:
            participant = Participant(
                nom=nom,
                prenom=prenom,
                email=email,
                sexe=sexe,
                age=int(age) if age else None,
                profession=profession
            )
            db.session.add(participant)
            db.session.commit()
            flash("Participant ajouté avec succès.", "success")
            print(f"Appel de register_participant avec les données : {request.form}")
            register_participant(request.form)
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", "danger")

        # Rediriger vers la même page avec l'event_id
        return redirect(url_for('manage_participants', event_id=event_id))

    # Récupérer tous les participants
    participants = Participant.query.all()
    return render_template('participants/manage.html', page_name='participants', participants=participants, event_id=event_id)

# Configuration de l'API GPT
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_random_participant():
    """Génère des données fictives pour un participant."""
    try:
        # Prompt pour GPT
        prompt = """
        Génère un profil fictif d'un participant à une conférence avec les informations suivantes. Respecte à la lettre les clés utilisées sans ajouter d'accent ou autre caracteres spéciaux:
        - Nom
        - Prenom
        - Sexe (Homme ou Femme)
        - Age (entre 18 et 65 ans)
        - Profession
        - Email (format valide)
        Retourne uniquement les informations sous forme de JSON.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un générateur de données fictives."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )

        participant_data = response.choices[0].message.content.strip()
        # Valider et parser les données
        try:
            participant_data = json.loads(participant_data)
            required_keys = {"Nom", "Prenom", "Sexe", "Age", "Profession", "Email"}
            if not required_keys.issubset(participant_data):
                raise ValueError(f"Données manquantes : {required_keys - participant_data.keys()}")
        except json.JSONDecodeError:
            raise ValueError("JSON invalide généré par GPT.")

        return jsonify(participant_data=json.dumps(participant_data)), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la génération des participants : {str(e)}"}), 500
    
def generate_random_demo_participant(number=5):
    """Génère des données fictives pour plusieurs participants et les ajoute à la base."""
    try:
        # Prompt pour GPT
        prompt = f"""
        Génère {number} profils fictifs de participants à une conférence avec les informations suivantes. Respecte à la lettre les clés utilisées sans ajouter d'accent ou autre caracteres spéciaux :
        - Nom
        - Prenom
        - Sexe (Homme ou Femme)
        - Age (entre 18 et 65 ans)
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

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un générateur de données fictives."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Augmenté pour permettre une réponse plus grande
        )

        raw_data = response.choices[0].message.content.strip()

        # Parse JSON et validation
        try:
            participants_data = json.loads(raw_data)
            if not isinstance(participants_data, list):
                raise ValueError("Le format attendu est une liste de dictionnaires.")
            required_keys = {"Nom", "Prenom", "Sexe", "Age", "Profession", "Email"}
            for participant in participants_data:
                if not required_keys.issubset(participant):
                    raise ValueError(f"Données manquantes dans un participant : {required_keys - participant.keys()}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide généré par GPT : {str(e)}")

        # Création des participants dans la base de données
        participants = []
        for participant_data in participants_data:
            participant = Participant(
                nom=participant_data["Nom"],
                prenom=participant_data["Prenom"],
                sexe=participant_data["Sexe"],
                age=participant_data["Age"],
                profession=participant_data["Profession"],
                email=participant_data["Email"]
            )
            db.session.add(participant)
            participants.append(participant)

        # Commit en une seule fois pour optimiser les performances
        db.session.commit()

        return jsonify(
            message=f"{len(participants)} participants créés avec succès.",
            participants=[{
                "id": p.id,
                "nom": p.nom,
                "prenom": p.prenom,
                "email": p.email
            } for p in participants]
        ), 200

    except Exception as e:
        db.session.rollback()  # Annuler les transactions en cas d'erreur
        return jsonify({"error": str(e)}), 500
    

def register_participant(data):
    """
    Enregistre un participant et envoie les données à un webhook Pipedream avec QR Code.
    """
    try:
        print("in send")
        # Récupérer les données
        email = data.get("email")
        nom = data.get("nom")
        prenom = data.get("prenom")
        age = data.get("age")

        # Validation des données
        if not all([email, nom, prenom]):
            return jsonify({"error": "Toutes les informations sont obligatoires."}), 400

        # Générer le QR Code
        qr_data = f"Participant: {prenom} {nom}, Email: {email}, ID: {age}"
        qr = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr.save(qr_buffer)
        qr_buffer.seek(0)

        # Encode QR code image en base64
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

        # Construire les données à envoyer au webhook
        payload = {
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "age": age,
            "qr_code": qr_base64
        }

        # URL du webhook Pipedream
        pipedream_url = "https://eou1r9maglcv9jv.m.pipedream.net"

        # Envoyer la requête au webhook
        response = requests.post(pipedream_url, json=payload)

        if response.status_code == 200:
            return jsonify({'message': 'Données envoyées au webhook avec succès.'}), 200
        else:
            return jsonify({'error': f"Erreur lors de l'envoi au webhook : {response.status_code} - {response.text}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def test_register():
    """
    Test de l'inscription d'un participant avec envoi d'email.
    """
    # Simuler les données d'inscription
    data = {
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "truc@gmail.com",  # Remplacez par votre email
        "sexe": "Homme",
        "age": 30,
        "profession": "Ingenieur"
    }

    # Appeler la fonction d'inscription
    return register_participant(data)