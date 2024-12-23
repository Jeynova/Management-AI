# Import des bibliothèques nécessaires
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fonction pour gérer l'historique du chat
def query_assistant_continuous(prompt):
    """Gère la continuité de la conversation avec l'IA."""
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Appeler OpenAI avec l'historique des messages
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    response = llm.predict_messages([
        SystemMessage(content="Tu es un assistant pour gérer les conférences."),
        *[
            HumanMessage(content=msg["content"])
            if msg["role"] == "user" else SystemMessage(content=msg["content"])
            for msg in st.session_state.messages
        ]
    ])

    # Ajouter la réponse de l'assistant à l'historique
    st.session_state.messages.append({"role": "assistant", "content": response.content})
    return response.content

# Fonction pour afficher l'historique
def display_chat_history():
    """Affiche l'historique du chat."""
    for message in st.session_state.messages:
        role = "👤 Utilisateur" if message["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{role}:** {message['content']}")

# Fonction pour réinitialiser l'historique
def reset_chat():
    """Réinitialise la conversation."""
    st.session_state.messages = []
    st.success("Conversation réinitialisée.")

# Section : Planification d'événement
if choice == "Planification d'événement":
    st.subheader("Planification d'événement")
    st.write("Entrez les détails pour planifier votre événement.")
    event_name = st.text_input("Nom de l'événement")
    dates = st.date_input("Dates importantes (par exemple, début et fin)")
    tasks = st.text_area("Quelles sont les grandes étapes à inclure ?")

    # Afficher l'historique du chat
    display_chat_history()

    # Entrée utilisateur pour continuer la conversation
    user_input = st.text_input("Posez votre question :", key="plan_event_input")
    if st.button("Envoyer", key="plan_event_submit"):
        if user_input.strip():
            response = query_assistant_continuous(f"[Planification] {user_input}")
            st.markdown(f"🤖 **Assistant:** {response}")

    # Réinitialisation de la conversation
    if st.button("Réinitialiser la conversation", key="plan_event_reset"):
        reset_chat()

    if st.button("Générer un plan"):
        prompt = f"""
        Tu es un expert en planification d'événements.
        Voici les détails de l'événement :
        - Nom : {event_name}
        - Dates : {dates}
        - Étapes : {tasks}
        
        Génère un plan complet avec des étapes claires et des suggestions.
        """
        response = query_assistant_continuous(prompt)
        st.write(response)

# Section : Création de contenu
elif choice == "Création de contenu":
    st.subheader("Création de contenu")
    st.write("Quel type de contenu voulez-vous créer ?")
    content_type = st.selectbox("Type de contenu :", ["Titre de session", "Description", "Email", "Biographie"])
    content_details = st.text_area("Donnez les détails nécessaires.")

    # Afficher l'historique du chat
    display_chat_history()

    # Entrée utilisateur pour continuer la conversation
    user_input = st.text_input("Posez votre question :", key="content_input")
    if st.button("Envoyer", key="content_submit"):
        if user_input.strip():
            response = query_assistant_continuous(f"[Création de contenu] {user_input}")
            st.markdown(f"🤖 **Assistant:** {response}")

    # Réinitialisation de la conversation
    if st.button("Réinitialiser la conversation", key="content_reset"):
        reset_chat()

    if st.button("Générer le contenu"):
        prompt = f"""
        Tu es un expert en communication événementielle. Crée un {content_type} basé sur ces détails :
        {content_details}
        """
        response = query_assistant_continuous(prompt)
        st.write(response)

# Section : Analyse de fichiers
elif choice == "Analyse de fichiers":
    st.subheader("Analyse de fichiers")
    uploaded_file = st.file_uploader("Téléchargez un fichier CSV pour analyse", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Aperçu des données :")
        st.write(df.head())

        # Afficher l'historique du chat
        display_chat_history()

        # Entrée utilisateur pour poser des questions sur le fichier
        user_input = st.text_input("Posez une question sur ce fichier :", key="file_input")
        if st.button("Envoyer", key="file_submit"):
            if user_input.strip():
                response = query_assistant_continuous(f"[Analyse de fichiers] {user_input}")
                st.markdown(f"🤖 **Assistant:** {response}")

        # Réinitialisation de la conversation
        if st.button("Réinitialiser la conversation", key="file_reset"):
            reset_chat()

# Section : Communication et marketing
elif choice == "Communication et marketing":
    st.subheader("Communication et marketing")
    st.write("Posez une question ou demandez des suggestions pour vos campagnes.")
    marketing_query = st.text_area("Votre question ou demande :")

    # Afficher l'historique du chat
    display_chat_history()

    # Entrée utilisateur pour continuer la conversation
    user_input = st.text_input("Posez votre question :", key="marketing_input")
    if st.button("Envoyer", key="marketing_submit"):
        if user_input.strip():
            response = query_assistant_continuous(f"[Communication et marketing] {user_input}")
            st.markdown(f"🤖 **Assistant:** {response}")

    # Réinitialisation de la conversation
    if st.button("Réinitialiser la conversation", key="marketing_reset"):
        reset_chat()

# Footer
st.divider()
st.caption("Bonne chance à tous pour votre validation. 🚀")
