from flask import jsonify, request, render_template, redirect, url_for, flash
from app.models import Visual, db, Conference
import openai
import os

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Utilitaires internes
def create_visual_prompt(details, context=None):
    """Construit un prompt professionnel pour la génération d'images."""
    base_prompt = f"""
    Concevez une image professionnelle et visuellement époustouflante pour un projet en suivant les détails suivants : 
    {details}. Assurez-vous que le design soit adapté aux supports numériques et imprimés, en respectant les principes 
    d'harmonie esthétique et de design graphique professionnel. Fournissez un résultat qui démontre créativité, 
    précision technique et innovation, comme si réalisé par un designer expert.
    """
    if context:
        base_prompt += f" Contexte supplémentaire : {context}."
    return base_prompt

def create_visual_iteration(new_description, context=None):
    # Créer le prompt basé sur le visuel précédent
    base_prompt = f"""
    Améliorez l'image de ce contexte {context}. 
    {new_description}. Maintenez un style professionnel et cohérent avec le thème initial, 
    en ajoutant des éléments qui accentuent son attrait visuel. Assurez-vous que le résultat soit 
    adapté aux supports numériques et imprimés.
    """
    if context:
        base_prompt += f" Contexte supplémentaire : {context}."
    return base_prompt

def generate_image(prompt):
    """Génère une image via DALL-E."""
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response["data"][0]["url"]

def save_visual_to_db(title, image_url, associated_type, associated_id):
    """Enregistre un visuel dans la base de données."""
    visual = Visual(
        title=title,
        image_url=image_url,
        associated_type=associated_type,
        associated_id=associated_id
    )
    db.session.add(visual)
    db.session.commit()
    return visual

# API : Génération de visuel
def generate_visual_api():
    """API pour générer un visuel via DALL-E."""
    try:
        data = request.json
        title = data.get("title", "Visuel pour conférence")
        prompt_details = data.get("prompt")
        associated_type = data.get("associated_type")  # 'conference' ou 'article'
        associated_id = data.get("associated_id")

        if not prompt_details:
            return jsonify({"error": "Le prompt est obligatoire."}), 400

        # Générer le visuel
        prompt = create_visual_prompt(prompt_details)
        image_url = generate_image(prompt)

        # Enregistrer dans la base de données
        visual = save_visual_to_db(title, image_url, associated_type, associated_id)

        return jsonify({
            "message": "Visuel généré avec succès.",
            "image_url": image_url,
            "visual_id": visual.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API : Itération sur un visuel existant
def iterate_visual_api():
    """API pour itérer sur un visuel existant."""
    try:
        data = request.json
        visual_id = data.get("visual_id")
        new_description = data.get("new_description", "Améliorer les détails.")

        # Vérifier l'existence du visuel
        visual = Visual.query.get(visual_id)
        if not visual:
            return jsonify({"error": "Visuel non trouvé."}), 404

        # Créer un nouveau visuel basé sur l'existant
        prompt = create_visual_iteration(new_description, context=f"Basé sur : {visual.image_url}")
        image_url = generate_image(prompt)

        # Enregistrer le nouveau visuel
        new_visual = save_visual_to_db(
            title=f"{visual.title} - Amélioré",
            image_url=image_url,
            associated_type=visual.associated_type,
            associated_id=visual.associated_id
        )

        return jsonify({
            "message": "Visuel amélioré avec succès.",
            "image_url": image_url,
            "visual_id": new_visual.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_visual_web():
    """Génère un visuel depuis l'interface web."""
    image_url = None  # Initialisation pour le rendu de la page

    if request.method == 'POST':
        title = request.form.get("title", "Visuel pour conférence")
        prompt_details = request.form.get("prompt")
        associated_type = request.form.get("associated_type")
        associated_id = request.form.get("associated_id")

        if not prompt_details:
            flash("Le prompt est obligatoire.", "danger")
        else:
            try:
                # Générer le visuel
                prompt = create_visual_prompt(prompt_details)
                image_url = generate_image(prompt)

                # Enregistrer dans la base de données
                save_visual_to_db(title, image_url, associated_type, associated_id)
                flash("Visuel généré avec succès !", "success")

            except Exception as e:
                flash(f"Erreur lors de la génération : {str(e)}", "danger")

    return render_template("generate.html", image_url=image_url)


# Web : Itération sur un visuel existant
def iterate_visual_web():
    """Itère sur un visuel depuis l'interface web."""
    image_url = None  # Initialisation pour le rendu de la page

    if request.method == 'POST':
        visual_id = request.form.get("visual_id")
        new_description = request.form.get("new_description", "Améliorer les détails.")

        visual = Visual.query.get(visual_id)
        if not visual:
            flash("Visuel non trouvé.", "danger")
        else:
            try:
                # Générer un nouveau visuel basé sur l'existant
                prompt = create_visual_iteration(new_description, context=f"Basé sur : {visual.image_url}")
                image_url = generate_image(prompt)

                # Enregistrer le nouveau visuel
                save_visual_to_db(
                    title=f"{visual.title} - Amélioré",
                    image_url=image_url,
                    associated_type=visual.associated_type,
                    associated_id=visual.associated_id
                )
                flash("Visuel amélioré avec succès !", "success")

            except Exception as e:
                flash(f"Erreur lors de l'amélioration : {str(e)}", "danger")

    return render_template("iterate.html", image_url=image_url)

# API : Liste des visuels
def list_visuals_api():
    """Liste tous les visuels en format JSON pour l'API."""
    try:
        visuals = Visual.query.all()
        visuals_list = [
            {
                "id": visual.id,
                "title": visual.title,
                "image_url": visual.image_url,
                "associated_type": visual.associated_type,
                "associated_id": visual.associated_id
            }
            for visual in visuals
        ]
        return jsonify({"visuals": visuals_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Web : Liste des visuels
def list_visuals_web():
    """Affiche tous les visuels dans une vue web."""
    try:
        visuals = Visual.query.all()
        return render_template("list.html", visuals=visuals)

    except Exception as e:
        return render_template("error.html", error=str(e))
