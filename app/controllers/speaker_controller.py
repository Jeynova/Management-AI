from flask import jsonify, request, url_for, flash, redirect, render_template
from app.models import Speaker, db
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def manage_speakers(event_id):
    """Affiche et gère les conférenciers existants."""
    if request.method == 'POST':
        # Ajouter un conférencier
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        age = request.form.get('age')
        sexe = request.form.get('sexe')
        profession = request.form.get('profession')
        bio = request.form.get('bio')

        try:
            speaker = Speaker(
                nom=nom,
                prenom=prenom,
                age=int(age) if age else None,
                sexe=sexe,
                profession=profession,
                bio=bio
            )
            db.session.add(speaker)
            db.session.commit()
            flash("Conférencier ajouté avec succès.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", "danger")

        return redirect(url_for('manage_speakers'))

    # Liste des conférenciers existants
    speakers = Speaker.query.all()
    return render_template('speakers/manage.html',page_name='speakers', speakers=speakers)

def regenerate_biography(speaker_id):
    """Régénère la biographie pour un orateur spécifique, même si elle existe déjà."""
    try:
        speaker = Speaker.query.get(speaker_id)
        if not speaker:
            return jsonify({"error": "Speaker non trouvé"}), 404

        # Prompt pour GPT
        prompt = f"""
        Tu es un rédacteur spécialisé en biographies professionnelles. Crée une biographie captivante 
        pour cet orateur basé sur les informations suivantes :
        - Nom : {speaker.prenom} {speaker.nom}
        - Profession : {speaker.profession}
        - Âge : {speaker.age or 'Non spécifié'}
        - Sexe : {speaker.sexe or 'Non spécifié'}
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un rédacteur expert en biographies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        bio = response.choices[0].message.content.strip()

        # Mettre à jour la biographie dans la base de données
        speaker.bio = bio
        db.session.commit()

        return jsonify({"message": "Biographie régénérée avec succès.", "bio": bio}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_biography(speaker_id):
    """Génère une biographie pour un orateur spécifique."""
    try:
        speaker = Speaker.query.get(speaker_id)
        if not speaker:
            return jsonify({"error": "Speaker non trouvé"}), 404
        
        # Vérifier si une biographie existe déjà
        if speaker.bio:
            return jsonify({"message": "La biographie existe déjà.", "bio": speaker.bio}), 200
        
        # Prompt pour GPT
        prompt = f"""
        Tu es un rédacteur spécialisé en biographies professionnelles. Crée une biographie captivante 
        pour cet orateur basé sur les informations suivantes :
        - Nom : {speaker.prenom} {speaker.nom}
        - Profession : {speaker.profession}
        - Âge : {speaker.age or 'Non spécifié'}
        - Sexe : {speaker.sexe or 'Non spécifié'}
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un rédacteur expert en biographies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        bio = response.choices[0].message.content.strip()

        # Enregistrer la biographie dans la base de données
        speaker.bio = bio
        db.session.commit()

        return jsonify({"message": "Biographie générée avec succès.", "bio": bio}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_biographies_bulk():
    """Génère des biographies pour tous les orateurs sans biographie."""
    try:
        speakers = Speaker.query.filter(Speaker.bio == None).all()  # Orateurs sans bio
        if not speakers:
            return jsonify({"message": "Aucun orateur sans biographie."}), 200

        generated_bios = []

        for speaker in speakers:
            # Prompt pour GPT
            prompt = f"""
            Tu es un rédacteur spécialisé en biographies professionnelles. Crée une biographie captivante 
            pour cet orateur basé sur les informations suivantes :
            - Nom : {speaker.prenom} {speaker.nom}
            - Profession : {speaker.profession}
            - Âge : {speaker.age or 'Non spécifié'}
            - Sexe : {speaker.sexe or 'Non spécifié'}
            """

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un rédacteur expert en biographies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            bio = response.choices[0].message.content.strip()

            # Enregistrer la biographie dans la base de données
            speaker.bio = bio
            db.session.add(speaker)
            generated_bios.append({"speaker_id": speaker.id, "bio": bio})

        db.session.commit()

        return jsonify({"message": "Biographies générées avec succès.", "generated_bios": generated_bios}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
