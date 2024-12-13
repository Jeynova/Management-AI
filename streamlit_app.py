# Import des bibliothèques nécessaires
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv, find_dotenv

# Charger la clé API OpenAI
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Configuration de la page
st.set_page_config(
    page_title="Assistant Admin Conférence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de la page
st.title("Assistant Admin - Gestion de Conférence 📅")

# Sidebar pour les options principales
with st.sidebar:
    st.header("Bienvenue dans l'Assistant Admin !")
    st.write("""
        Cet assistant virtuel vous aide à organiser et gérer votre conférence technologique. 
        Il est conçu pour être flexible et s'adapter à vos besoins spécifiques :
        - **Planification d'événements**
        - **Création de contenu**
        - **Analyse de fichiers**
        - **Communication et marketing**
    """)
    st.caption("Posez vos questions ou téléversez des fichiers pour commencer !")

    # Options principales dans la barre latérale
    st.header("Que voulez-vous faire ?")
    choice = st.selectbox(
        "Choisissez une tâche :",
        ["Planification d'événement", "Création de contenu", "Analyse de fichiers", "Communication et marketing"]
    )

# Fonction pour envoyer une question à l'assistant
def query_assistant(prompt):
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    messages = [
        SystemMessage(content="Tu es un assistant spécialisé dans la création de contenu pour des conférences."),
        HumanMessage(content=prompt),
    ]
    response = llm.predict_messages(messages)
    return response.content  # Récupère uniquement le texte de la réponse

# Fonction pour analyser un fichier téléversé
def analyze_file(df):
    st.write("**Aperçu des données**")
    st.write(df.head())

    # Agent Pandas pour l'analyse
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    pandas_agent = create_pandas_dataframe_agent(
        llm, df, verbose=True, allow_dangerous_code=True, handle_parsing_errors=True
    )

    # Menu déroulant pour les analyses
    analysis_choice = st.selectbox(
        "Choisissez une analyse à effectuer :",
        [
            "Résumé global",
            "Tendances et projections",
            "Corrélations entre variables",
            "Graphiques",
        ]
    )

    if analysis_choice == "Résumé global":
        try:
            summary = pandas_agent.run(
                """
                Analyse ce tableau en français. Fournis une analyse complète en expliquant :
                - L'utilité du tableau.
                - Les observations détaillées tirées des données.
                - Des recommandations exploitables.
                Réponds de manière professionnelle et exhaustive en français.
                """
            )
            st.write("**Résumé global :**")
            st.write(summary)
        except ValueError as e:
            st.error("Une erreur s'est produite lors de l'analyse automatique.")
            st.exception(e)

    elif analysis_choice == "Tendances et projections":
        try:
            trends = pandas_agent.run(
                """
                Identifie les tendances majeures et propose des projections exploitables en français. Explique clairement avec des exemples
                tirés des données.
                """
            )
            st.write("**Tendances et projections :**")
            st.write(trends)
        except ValueError as e:
            st.error("Une erreur s'est produite lors de l'analyse des tendances.")
            st.exception(e)

    elif analysis_choice == "Corrélations entre variables":
        try:
            correlations = pandas_agent.run(
                """
                Calcule les corrélations entre les variables. Explique les relations significatives et comment elles peuvent
                être exploitées. Réponds en français et de manière claire.
                """
            )
            st.write("**Corrélations entre variables :**")
            st.write(correlations)
        except ValueError as e:
            st.error("Une erreur s'est produite lors de l'analyse des corrélations.")
            st.exception(e)

    elif analysis_choice == "Graphiques":
        st.write("**Création de Graphiques :**")
        # Exemple : Répartition des participants par pays
        if "Pays" in df.columns:
            country_counts = df["Pays"].value_counts()
            st.write("**Répartition des participants par pays :**")
            fig, ax = plt.subplots()
            country_counts.plot(kind="bar", ax=ax)
            ax.set_title("Répartition des participants par pays")
            ax.set_ylabel("Nombre de participants")
            ax.set_xlabel("Pays")
            st.pyplot(fig)
        else:
            st.warning("La colonne 'Pays' n'est pas disponible pour créer ce graphique.")

# Gestion des choix
if choice == "Planification d'événement":
    st.subheader("Planification d'événement")
    st.write("Entrez les détails pour planifier votre événement.")
    event_name = st.text_input("Nom de l'événement")
    dates = st.date_input("Dates importantes (par exemple, début et fin)")
    tasks = st.text_area("Quelles sont les grandes étapes à inclure ?")

    if st.button("Générer un plan"):
        prompt = f"""
        Tu es un expert en planification d'événements.
        Voici les détails de l'événement :
        - Nom : {event_name}
        - Dates : {dates}
        - Étapes : {tasks}
        
        Génère un plan complet avec des étapes claires et des suggestions.
        """
        response = query_assistant(prompt)
        st.write(response)

elif choice == "Création de contenu":
    st.subheader("Création de contenu")
    st.write("Quel type de contenu voulez-vous créer ?")
    content_type = st.selectbox("Type de contenu :", ["Titre de session", "Description", "Email", "Biographie"])
    content_details = st.text_area("Donnez les détails nécessaires.")

    if st.button("Générer le contenu"):
        prompt = f"""
        Tu es un expert en communication événementielle. Crée un {content_type} basé sur ces détails :
        {content_details}
        """
        response = query_assistant(prompt)
        st.write(response)

elif choice == "Analyse de fichiers":
    st.subheader("Analyse de fichiers")
    uploaded_file = st.file_uploader("Téléchargez un fichier CSV pour analyse", type=["csv"])

    if uploaded_file:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        analyze_file(df)

elif choice == "Communication et marketing":
    st.subheader("Communication et marketing")
    st.write("Posez une question ou demandez des suggestions pour vos campagnes.")
    marketing_query = st.text_area("Votre question ou demande :")

    if st.button("Obtenir des conseils"):
        prompt = f"""
        Tu es un expert en communication et marketing événementiel. Voici la situation :
        {marketing_query}
        Fournis des recommandations et des stratégies adaptées.
        """
        response = query_assistant(prompt)
        st.write(response)

# Footer
st.divider()
st.caption("Bonne chance à tous pour votre validation. 🚀")
