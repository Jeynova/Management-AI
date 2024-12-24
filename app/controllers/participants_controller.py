from flask import render_template, request, redirect, url_for, flash
from app.models import Participant, db
import os

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
    return render_template('participants/manage.html', participants=participants)

import openai
import random
from flask import jsonify

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