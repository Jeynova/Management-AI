import os
import requests
from flask import render_template, request, redirect, url_for, flash,jsonify, request
from app.models import Visual, db
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv


load_dotenv()

# Configuration de l'API OpenAI et du dossier de sauvegarde
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("La clé API OpenAI n'est pas définie dans les variables d'environnement.")
client = OpenAI(api_key=openai_api_key)
IMAGE_FOLDER = os.path.join("app", "static", "images", "visuals")

def save_image_locally(image_content, filename):
    filepath = os.path.join(IMAGE_FOLDER, filename).replace("\\", "/")

    try:
        # Écrire directement le contenu de l'image
        with open(filepath, "wb") as file:
            file.write(image_content)
        print(f"Image enregistrée avec succès à : {filepath}")
        return filepath
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'image : {e}")
        raise e

def manage_visuals(event_id=None):
    if event_id:
        visuals = Visual.query.filter_by(evenement_id=event_id).all()
    else:
        visuals = Visual.query.all()
    

    """Affiche et gère les visuels existants."""
    if request.method == 'POST':
        # Création d'un nouveau visuel
        title = request.form.get('title')
        prompt = request.form.get('prompt')
        associated_type = request.form.get('associated_type')
        associated_id = request.form.get('associated_id')

        # Utiliser la fonction generate_visual
        response = generate_visual(title=title, prompt=prompt, associated_type=associated_type, associated_id=associated_id)

        if response.status_code == 200:
            flash("Visuel généré avec succès.", "success")
        else:
            flash("Erreur lors de la génération du visuel.", "danger")

        return redirect(url_for('manage_visuals', event_id=event_id))

    # Liste des visuels existants
    visuals = Visual.query.all()
    return render_template('visuals/manage.html', page_name='visuals', visuals=visuals,event_id=event_id)

def generate_visual():
    """Génère un visuel via DALL·E et l'enregistre dans la base de données."""
    try:
        # Récupérer les données de la requête
        data = request.json
        title = data.get("title", "Visuel pour conférence")
        prompt_details = data.get("prompt")
        associated_type = data.get("associated_type")  # 'conference' ou 'article'
        associated_id = data.get("associated_id")

        if not prompt_details:
            return jsonify({"error": "Le prompt est obligatoire."}), 400

        # Construire un prompt professionnel
        prompt = (
            #f"Concevez une image professionnelle et visuellement époustouflante pour un projet. "
            #f"{prompt_details}. Assurez-vous que le design reflète créativité, précision technique et "
            #f"innovation, en démontrant une harmonie esthétique propre à un expert en design graphique."
            #f"Concevez une image professionnelle et visuellement époustouflante pour une conférence."

            f"Votre tâche est de créer une image de haute qualité en fonction des spécifications suivantes."
            f"- **Details** : Inclure des éléments qui sont {prompt_details}"
            f"- **Critères** : Assurez-vous que le design soit adapté aux supports numériques et imprimés. Respectez les principes d'harmonie esthétique et de design graphique professionnel."
            f"- **Objectif** : Le résultat doit démontrer créativité, précision technique, et innovation, comme si réalisé par un designer expert."

            # Steps

            f"1. Comprendre les details demandés."
            f"2. Concevoir l'image en tenant compte de l'adaptation aux supports numériques et imprimés."
            f"3. Intégrer des éléments spécifiques décrits pour refléter le style défini."
            f"4. Veiller à une harmonie esthétique et au professionnalisme du design graphique."
            f"5. Finaliser le visuel en s'assurant qu'il montre créativité, précision et innovation."

            # Output Format

            f"- Le design doit être présenté dans un format visuel apte à être affiché à la fois numériquement et imprimé."
            f"- Assurez-vous que tous les détails visuels sont clairs et bien structurés."

            # Notes

            f"- Soyez attentif aux proportions et à l'équilibre des couleurs."
            f"- Évitez les surcharges graphiques tout en maintenant une clarté visuelle."
            f"- Pensez à l'originalité tout en restant dans les limites professionnelles du design."
        )

        # Appeler DALL·E pour générer un visuel
        generation_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url",
            quality="hd"
        )

        image_url = generation_response.data[0].url

        # Télécharger l'image générée
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            return jsonify({"error": "Erreur lors du téléchargement de l'image générée."}), 500

        # Enregistrer l'image localement
        image_filename = f"{title.replace(' ', '_')}.png"
        print(f"Nom de fichier généré : {image_filename}")  # Debug
        image_path = save_image_locally(image_response.content, image_filename)
        print(f"Image enregistrée à : {image_path}")  # Debug

        # Créer un nouvel objet Visual
        visual = Visual(
            title=title,
            image_url=image_path.split('app/', 1)[-1],  # Enregistrer le chemin local au lieu de l'URL temporaire
            associated_type=associated_type,
            associated_id=associated_id
        )
        db.session.add(visual)
        db.session.commit()

        return jsonify({
            "message": "Visuel généré avec succès.",
            "image_url": url_for('static', filename=image_path.split('static/', 1)[-1], _external=True),
            "visual_id": visual.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500