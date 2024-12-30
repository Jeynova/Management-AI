import pandas as pd
import openai
import streamlit as st
import numpy as np
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Chargement du fichier SVG
svg_file_path = "static/images/sources/logo.svg"
with open(svg_file_path, "r", encoding="utf-8") as svg_file:
    svg_logo = svg_file.read()

# Configuration de la page Streamlit
st.set_page_config(page_title="Assistant d'analyse de données hybride", page_icon=":bar_chart:", layout="centered")

# Fonction pour afficher la barre latérale
def afficher_sidebar():
    st.sidebar.title('À propos')
    st.sidebar.info('''
        Cette application utilise l'[API OpenAI](https://platform.openai.com/docs/overview) pour générer des réponses aux questions sur les fichiers de données.
    ''')
    st.sidebar.title('Guide')
    st.sidebar.info('''
        1. Téléchargez un fichier de données au format CSV ou Excel.
        2. Sélectionnez une analyse dans le menu déroulant.
        3. Cliquez sur le bouton "Générer une réponse".
    ''')
    st.sidebar.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <span style="font-size: 16px; font-weight: bold; margin-right: 10px;">Réalisé pour</span>
            <div>{svg_logo}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Fonctions d'analyse locale
def apercu_du_fichier(df):
    st.write(f"Le fichier contient {df.shape[0]} lignes et {df.shape[1]} colonnes.")
    st.write("Aperçu des types de données :")
    st.write(df.dtypes)

def valeurs_manquantes(df):
    missing_values = df.isnull().sum()
    st.write("Résumé des valeurs manquantes par colonne :")
    st.write(missing_values[missing_values > 0])

def resume_statistique(df):
    st.write("Résumé statistique des colonnes numériques :")
    st.write(df.describe().transpose())

def resume_categoriel(df):
    categorical_cols = df.select_dtypes(include=['object', 'category'])
    for col in categorical_cols.columns:
        st.write(f"Colonne : {col}")
        st.write(categorical_cols[col].value_counts())
        st.write("")

def calculer_correlations(df):
    # Sélectionner uniquement les colonnes numériques
    df_numerique = df.select_dtypes(include=[np.number])
    
    # Vérifier s'il y a des colonnes numériques
    if df_numerique.empty:
        st.write("Aucune colonne numérique disponible pour calculer les corrélations.")
    else:
        # Calculer la matrice de corrélation
        matrice_correlation = df_numerique.corr()
        st.write("Matrice de corrélation entre les colonnes numériques :")
        st.write(matrice_correlation)
        return matrice_correlation

# Fonction pour interagir avec GPT-4
def analyse_par_gpt4(question, contexte):
    prompt = f"{question}\n\nVoici les données d'analyse :\n{contexte}"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Vous êtes un assistant expert en analyse de données. Votre rôle est de fournir des réponses claires, "
                    "professionnelles et détaillées à des questions spécifiques sur les données. Expliquez vos conclusions "
                    "avec précision et fournissez des recommandations exploitables lorsque cela est pertinent. Adoptez un ton neutre "
                    "et professionnel tout en étant compréhensible. Si des hypothèses sont nécessaires pour répondre, "
                    "précisez-les explicitement. Structurez votre réponse pour qu'elle soit facilement lisible, en utilisant des sections ou "
                    "des listes pour clarifier les points clés."
                )
            },

            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

# Fonction pour analyser et interpréter les résultats via GPT-4
def analyser_et_interpreter_avec_gpt4(question, contexte):
    st.write("Analyse des résultats par GPT-4...")
    reponse_gpt = analyse_par_gpt4(question, contexte)
    
    # Diviser la réponse brute en parties pour éviter la répétition
    lignes = reponse_gpt.split('\n')
    recommandations = []
    contenu_general = []

    for ligne in lignes:
        if "recommandation" in ligne.lower() or "analyse" in ligne.lower():
            recommandations.append(ligne)
        else:
            contenu_general.append(ligne)

    # Affichage structuré
    if contenu_general:
        st.write("Analyse générale :")
        for ligne in contenu_general:
            st.write(ligne)

    if recommandations:
        st.write("Recommandations importantes :")
        for ligne in recommandations:
            st.markdown(f"<span style='color: red;'>{ligne}</span>", unsafe_allow_html=True)

# Initialisation de l'historique des messages pour le chat continu
if "messages" not in st.session_state:
    st.session_state.messages = []  # Liste pour stocker les messages (questions/réponses)

def afficher_chat_principal():
    """Affiche le chat principal avec style conversationnel sans répétition."""
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
                <div style='display: flex; align-items: flex-end; margin-bottom: 10px;'>
                    <div style='background-color: #333333; color: white; padding: 10px; border-radius: 10px; max-width: 80%; margin-left: auto;'>
                        <b>Vous :</b><br>{message['content']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif message["role"] == "assistant":
            st.markdown(f"**GPT-4 :** {message['content']}")

# Fonction pour gérer le chat continu avec GPT-4
def query_assistant_continuous(prompt, dataframe):
    """Gère la continuité de la conversation avec GPT-4 en incluant le contexte du fichier."""
    # Vérifier si le message utilisateur est déjà dans l'historique
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

    # Construire un contexte à partir du fichier
    contexte_fichier = (
        f"Le fichier contient {dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes. "
        f"Voici les 5 premières lignes :\n{dataframe.head().to_string(index=False)}\n\n"
    )

    # Appeler OpenAI avec l'historique des messages et le contexte
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
            "role": "system",
            "content": (
                "Vous êtes un assistant expert en analyse de données. Posez les questions nécessaires pour définir "
                "l'objectif et le type d'analyse (Descriptive, Diagnostique, Prédictive, Prescriptive, ou autre). "
                "Adaptez votre analyse aux points clés spécifiés par l'utilisateur, en procédant étape par étape selon "
                "ses retours. Utilisez des méthodes statistiques appropriées, nettoyez les données, et fournissez des "
                "recommandations exploitables. Documentez chaque étape pour assurer transparence et clarté."
            )
        },
            {"role": "system", "content": contexte_fichier},
            *st.session_state.messages
        ]
    )

    # Ajouter la réponse de l'assistant à l'historique uniquement si elle est nouvelle
    assistant_response = response.choices[0].message.content
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != assistant_response:
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    return assistant_response

    # Ajouter la réponse de l'assistant à l'historique
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content

# Fonction principale de l'application
def run_app():
    st.title("Assistant d'analyse de données hybride")

    # Téléchargement du fichier de données
    fichier = st.file_uploader("Téléchargez votre fichier de données", type=["csv", "xlsx"])

    if fichier:
        if fichier.name.endswith('.csv'):
            df = pd.read_csv(fichier)
        else:
            df = pd.read_excel(fichier)

        # Sélection de l'analyse
        option = st.selectbox("Choisissez une analyse", [
            "Aperçu du fichier (Structure générale des données)",
            "Valeurs manquantes (Colonnes avec des données manquantes)",
            "Résumé statistique (Analyse des chiffres clés, moyenne, médiane, etc.)",
            "Résumé catégoriel (Fréquences des catégories dans les colonnes textuelles)",
            "Corrélations (Relations entre colonnes numériques)",
            "Analyse automatisée des résultats (Interprétation automatique avec GPT-4)",
            "Posez vos propres questions ponctuelles à GPT-4",
            "Chat Continu avec GPT-4"
        ])

        if st.button("Générer une réponse"):
            with st.spinner('Génération de la réponse...'):
                if option == "Aperçu du fichier (Structure générale des données)":
                    apercu_du_fichier(df)
                elif option == "Valeurs manquantes (Colonnes avec des données manquantes)":
                    valeurs_manquantes(df)
                elif option == "Résumé statistique (Analyse des chiffres clés, moyenne, médiane, etc.)":
                    resume_statistique(df)
                elif option == "Résumé catégoriel (Fréquences des catégories dans les colonnes textuelles)":
                    resume_categoriel(df)
                elif option == "Corrélations (Relations entre colonnes numériques)":
                    calculer_correlations(df)
                elif option == "Analyse automatisée des résultats (Interprétation automatique avec GPT-4)":
                    # Analyse GPT-4 automatique
                    data = {
                        "corrélations": calculer_correlations(df).to_dict() if not df.select_dtypes(include=[np.number]).empty else None,
                        "résumé_statistique": df.describe().transpose().to_dict(),
                        "résumé_catégoriel": {col: df[col].value_counts().to_dict() for col in df.select_dtypes(include=['object', 'category']).columns}
                    }
                    reponse = analyse_par_gpt4(
                        "Analysez les corrélations, résumés statistiques et catégoriels de ces données et proposez des recommandations.",
                        data
                    )
                    st.write("Résultat généré par GPT-4 :")
                    st.write(reponse)
                elif option == "Posez vos propres questions ponctuelles à GPT-4":
                    # Posez une question unique à GPT-4
                    question = st.text_input("Entrez votre question pour GPT-4", "")
                    if st.button("Envoyer"):
                        if question.strip():
                            contexte = df.head().to_dict()
                            reponse = analyse_par_gpt4(
                                f"Voici un aperçu des données : {contexte}\n\n{question}",
                                {}
                            )
                            st.write("Réponse de GPT-4 :")
                            st.write(reponse)
                        else:
                            st.error("Veuillez entrer une question avant de cliquer sur le bouton.")
                elif option == "Chat Continu avec GPT-4":
                    # Chat continu avec GPT-4
                    user_input = st.text_input("Posez une question à GPT-4 :", "")
                    if st.button("Envoyer"):
                        if user_input.strip():
                            with st.spinner("GPT-4 réfléchit..."):
                                reponse = query_assistant_continuous(user_input)
                            st.write(f"**Vous :** {user_input}")
                            st.write(f"**GPT-4 :** {reponse}")
                        else:
                            st.error("Veuillez entrer une question avant d'envoyer.")

                    # Afficher l'historique complet
                    st.write("### Historique de la conversation")
                    for message in st.session_state.messages:
                        if message["role"] == "user":
                            st.write(f"**Vous :** {message['content']}")
                        elif message["role"] == "assistant":
                            st.write(f"**GPT-4 :** {message['content']}")

# Exécution de l'application
if __name__ == '__main__':
    afficher_sidebar()
    run_app()