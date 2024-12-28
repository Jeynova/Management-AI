from flask import render_template, request, redirect, url_for, flash
from app.models import Participant, db
import os
import openai
import random
from flask import jsonify
import json

def manage_participants():
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
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", "danger")

        return redirect(url_for('manage_participants'))

    # Récupérer tous les participants
    participants = Participant.query.all()
    return render_template('participants/manage.html',page_name='participants', participants=participants)


# Configuration de l'API GPT
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_random_participant():
    """Génère des données fictives pour un participant."""
    try:
        # Prompt pour GPT
        prompt = """
        Génère un profil fictif d'un participant à une conférence avec les informations suivantes :
        - Nom
        - Prénom
        - Sexe (Homme ou Femme)
        - Âge (entre 18 et 65 ans)
        - Profession
        - Email (format valide)
        Retourne les informations sous forme de JSON.
        Voici un exemple de structure : 
                    {
            "Nom": "Dupont",
            "Prenom": "Jean",
            "Sexe": "Homme",
            "Age": 40,
            "Profession": "Ingénieur en informatique",
            "Email": "jean.dupont@email.com"
            }
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
        return jsonify(participant_data=participant_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def generate_random_demo_participant(number=5):
    """Génère des données fictives pour plusieurs participants et les ajoute à la base."""
    try:
        # Prompt pour GPT
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