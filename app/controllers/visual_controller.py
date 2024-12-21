import os
import requests
from flask import jsonify, request
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

IMAGE_FOLDER = os.path.join("static", "images", "visuals")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def save_image_locally(image_content, filename):
    """Enregistre l'image à partir du contenu binaire."""
    filepath = os.path.join(IMAGE_FOLDER, filename)
    with open(filepath, "wb") as file:
        file.write(image_content)
    return filepath

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
        )

        image_url = generation_response.data[0].url

        # Télécharger l'image générée
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            return jsonify({"error": "Erreur lors du téléchargement de l'image générée."}), 500

        # Enregistrer l'image localement
        image_filename = f"{title.replace(' ', '_')}.png"
        image_path = save_image_locally(image_response.content, image_filename)

        # Créer un nouvel objet Visual
        visual = Visual(
            title=title,
            image_url=image_path,  # Enregistrer le chemin local au lieu de l'URL temporaire
            associated_type=associated_type,
            associated_id=associated_id
        )
        db.session.add(visual)
        db.session.commit()

        return jsonify({
            "message": "Visuel généré avec succès.",
            "image_url": image_url,
            "visual_id": visual.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def iterate_visual():
    """Itère sur un visuel existant en générant une nouvelle version et l'enregistre."""
    try:
        # Récupérer les données de la requête
        data = request.json
        visual_id = data.get("visual_id")
        new_description = data.get("new_description", "Améliorer les détails.")

        # Vérifier que le visuel existe
        visual = Visual.query.get(visual_id)
        if not visual:
            return jsonify({"error": "Visuel non trouvé."}), 404

        # Télécharger l'image existante
        image_response = requests.get(visual.image_url)
        if image_response.status_code != 200:
            return jsonify({"error": "Erreur lors du téléchargement de l'image existante."}), 500

        # Enregistrer l'image localement pour la modification
        original_image_path = save_image_locally(image_response.content, f"original_{visual_id}.png")

        # Charger l'image avec PIL
        original_image = Image.open(original_image_path)

        # Créer un masque vierge (à adapter selon les besoins)
        mask = Image.new("RGBA", original_image.size, (0, 0, 0, 0))
        mask_path = os.path.join(IMAGE_FOLDER, f"mask_{visual_id}.png")
        mask.save(mask_path)

        # Appeler DALL·E pour éditer le visuel
        with open(original_image_path, "rb") as image_file, open(mask_path, "rb") as mask_file:
            edit_response = client.images.edits(
                model="dall-e-2",
                image=image_file.read(),
                mask=mask_file.read(),
                prompt=(
                    #f"Améliorez l'image existante. {new_description}. Maintenez un style professionnel et cohérent "
                    #f"avec le thème initial, en ajoutant des éléments qui accentuent son attrait visuel. Assurez-vous "
                    #f"que le résultat soit adapté aux supports numériques et imprimés."

                    f"Améliorez un visuel existant en mettant à jour son design pour inclure de nouvelles descriptions tout en restant cohérent avec son style initial."
                    f"Assurez-vous que le résultat reflète un style professionnel, en mettant l'accent sur les thèmes d'innovation et de technologie. Agissez en tant que designer expert pour produire un résultat raffiné et captivant."

                    # Étapes

                    f"1. **Analyse du visuel original** : Examinez l'image existante pour comprendre son style, sa composition et ses palettes de couleurs actuelles."
                    f"2. **Incorporation de la nouvelle description** : Intégrez {new_description} de manière fluide en respectant le thème existant."
                    f"3. **Cohérence et équilibre** : Assurez une harmonie visuelle où les éléments nouveaux et existants se complètent."
                    f"4. **Thèmes d'innovation et technologie** : Renforcez ces thèmes en utilisant des éléments de design modernes et technologiquement inspirés."
                    f"5. **Révision finale** : Vérifiez la cohérence générale et le professionnalisme du visuel."

                    # Format de Sortie

                    f"Décrivez les modifications apportées sous la forme d'une liste concise, énumérant les éléments mis à jour et les raisons de ces changements pour maintenir l'alignement stylistique et thématique."

                    # Exemples

                    f"**Exemple 1** :"
                    f"- **Visuel Original** : Brochure d'une entreprise technologique."
                    f"- **Nouvelle Description** : Ajouter un paragraphe sur une nouvelle IA."
                    f"- **Modifications** :"
                    f"- Ajout d'une section 'Innovations en IA'."
                    f"- Utilisation de couleurs bleu et argent pour maintenir un thème technologique."
                    f"- Insertion d'icônes technologiques modernes pour souligner le sujet."

                    f"**Exemple 2** :"
                    f"- **Visuel Original** : Affiche pour une conférence sur les nouvelles technologies."
                    f"- **Nouvelle Description** : Inclure un profil d'orateur invité."
                    f"- **Modifications** :"
                    f"- Ajout d'une image de l'orateur avec une courte biographie."
                    f"- Utilisation de typographies modernes pour attirer l'attention."
                    f"- Ajustement de la mise en page pour intégrer les nouvelles informations sans surcharger l'affiche."

                    # Notes

                    f"- Soyez attentif aux détails comme la typographie, l'espacement, et la répartition des couleurs pour maintenir 'l'unité visuelle'."
                    f"- Les thèmes d'innovation et de technologie doivent toujours guider vos choix de design."
                ),
                n=1,
                size="1024x1024",
                response_format="url",
            )

        edited_image_url = edit_response.data[0].url

        # Télécharger l'image éditée
        edited_image_response = requests.get(edited_image_url)
        if edited_image_response.status_code != 200:
            return jsonify({"error": "Erreur lors du téléchargement de l'image éditée."}), 500

        # Enregistrer l'image éditée localement
        edited_image_filename = f"{visual.title.replace(' ', '_')}_ameliore.png"
        edited_image_path = save_image_locally(edited_image_response.content, edited_image_filename)

        # Créer un nouvel objet Visual pour le visuel amélioré
        new_visual = Visual(
            title=f"{visual.title} - Amélioré",
            image_url=edited_image_path,
            associated_type=visual.associated_type,
            associated_id=visual.associated_id
        )
        db.session.add(new_visual)
        db.session.commit()

        return jsonify({
            "message": "Visuel amélioré avec succès.",
            "image_url": edited_image_url,
            "visual_id": new_visual.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
