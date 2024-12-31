# Import des biblioth√®ques n√©cessaires
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv, find_dotenv

# Charger la cl√© API OpenAI
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Configuration de la page
st.set_page_config(
    page_title="Assistant Admin Conf√©rence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de la page
st.title("Assistant Admin - Gestion de Conf√©rence üìÖ")

# Sidebar pour les options principales
with st.sidebar:
    st.header("Bienvenue dans l'Assistant Admin !")
    st.write("""
        Cet assistant virtuel vous aide √† organiser et g√©rer votre conf√©rence technologique. 
        Il est con√ßu pour √™tre flexible et s'adapter √† vos besoins sp√©cifiques :
        - **Planification d'√©v√©nements**
        - **Cr√©ation de contenu**
        - **Analyse de fichiers**
        - **Communication et marketing**
    """)
    st.caption("Posez vos questions ou t√©l√©versez des fichiers pour commencer !")

    # Options principales dans la barre lat√©rale
    st.header("Que voulez-vous faire ?")
    choice = st.selectbox(
        "Choisissez une t√¢che :",
        ["Planification d'√©v√©nement", "Cr√©ation de contenu", "Analyse de fichiers", "Communication et marketing"]
    )

# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fonction pour g√©rer l'historique du chat
def query_assistant_continuous(prompt):
    """G√®re la continuit√© de la conversation avec l'IA."""
    # Ajouter le message utilisateur √† l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Appeler OpenAI avec l'historique des messages
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    response = llm.predict_messages([
        SystemMessage(content="Tu es un assistant pour g√©rer les conf√©rences."),
        *[
            HumanMessage(content=msg["content"])
            if msg["role"] == "user" else SystemMessage(content=msg["content"])
            for msg in st.session_state.messages
        ]
    ])

    # Ajouter la r√©ponse de l'assistant √† l'historique
    st.session_state.messages.append({"role": "assistant", "content": response.content})
    return response.content

# Fonction pour afficher l'historique
def display_chat_history():
    """Affiche l'historique du chat."""
    for message in st.session_state.messages:
        role = "üë§ Utilisateur" if message["role"] == "user" else "ü§ñ Assistant"
        st.markdown(f"**{role}:** {message['content']}")

# Fonction pour r√©initialiser l'historique
def reset_chat():
    """R√©initialise la conversation."""
    st.session_state.messages = []
    st.success("Conversation r√©initialis√©e.")

# Section : Planification d'√©v√©nement
if choice == "Planification d'√©v√©nement":
    st.subheader("Planification d'√©v√©nement")
    st.write("Entrez les d√©tails pour planifier votre √©v√©nement.")
    event_name = st.text_input("Nom de l'√©v√©nement")
    dates = st.date_input("Dates importantes (par exemple, d√©but et fin)")
    tasks = st.text_area("Quelles sont les grandes √©tapes √† inclure ?")

    # Afficher l'historique du chat
    display_chat_history()

    # Entr√©e utilisateur pour continuer la conversation
    user_input = st.text_input("Posez votre question :", key="plan_event_input")
    if st.button("Envoyer", key="plan_event_submit"):
        if user_input.strip():
            response = query_assistant_continuous(f"[Planification] {user_input}")
            st.markdown(f"ü§ñ **Assistant:** {response}")

    # R√©initialisation de la conversation
    if st.button("R√©initialiser la conversation", key="plan_event_reset"):
        reset_chat()

    if st.button("G√©n√©rer un plan"):
        prompt = f"""
        Tu es un expert en planification d'√©v√©nements.
        Voici les d√©tails de l'√©v√©nement :
        - Nom : {event_name}
        - Dates : {dates}
        - √âtapes : {tasks}
        
        G√©n√®re un plan complet avec des √©tapes claires et des suggestions.
        """
        response = query_assistant_continuous(prompt)
        st.write(response)

# Section : Cr√©ation de contenu
elif choice == "Cr√©ation de contenu":
    st.subheader("Cr√©ation de contenu")
    st.write("Quel type de contenu voulez-vous cr√©er ?")
    content_type = st.selectbox("Type de contenu :", ["Titre de session", "Description", "Email", "Biographie"])
    content_details = st.text_area("Donnez les d√©tails n√©cessaires.")

    # Afficher l'historique du chat
    display_chat_history()

    # Entr√©e utilisateur pour continuer la conversation
    user_input = st.text_input("Posez votre question :", key="content_input")
    if st.button("Envoyer", key="content_submit"):
        if user_input.strip():
            response = query_assistant_continuous(f"[Cr√©ation de contenu] {user_input}")
            st.markdown(f"ü§ñ **Assistant:** {response}")

    # R√©initialisation de la conversation
    if st.button("R√©initialiser la conversation", key="content_reset"):
        reset_chat()

    if st.button("G√©n√©rer le contenu"):
        prompt = f"""
        Tu es un expert en communication √©v√©nementielle. Cr√©e un {content_type} bas√© sur ces d√©tails :
        {content_details}
        """
        response = query_assistant_continuous(prompt)
        st.write(response)

# Section : Analyse de fichiers
elif choice == "Analyse de fichiers":
    st.subheader("Analyse de fichiers")
    uploaded_file = st.file_uploader("T√©l√©chargez un fichier CSV pour analyse", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Aper√ßu des donn√©es :")
        st.write(df.head())

        # Afficher l'historique du chat
        display_chat_history()

        # Entr√©e utilisateur pour poser des questions sur le fichier
        user_input = st.text_input("Posez une question sur ce fichier :", key="file_input")
        if st.button("Envoyer", key="file_submit"):
            if user_input.strip():
                response = query_assistant_continuous(f"[Analyse de fichiers] {user_input}")
                st.markdown(f"ü§ñ **Assistant:** {response}")

        # R√©initialisation de la conversation
        if st.button("R√©initialiser la conversation", key="file_reset"):
            reset_chat()

# Section : Communication et marketing
elif choice == "Communication et marketing":
    st.subheader("Communication et marketing")
    st.write("Posez une question ou demandez des suggestions pour vos campagnes.")
    marketing_query = st.text_area("Votre question ou demande :")

    # Afficher l'historique du chat
    display_chat_history()

    # Entr√©e utilisateur pour continuer la conversation
    user_input = st.text_input("Posez votre question :", key="marketing_input")
    if st.button("Envoyer", key="marketing_submit"):
        if user_input.strip():
            response = query_assistant_continuous(f"[Communication et marketing] {user_input}")
            st.markdown(f"ü§ñ **Assistant:** {response}")

    # R√©initialisation de la conversation
    if st.button("R√©initialiser la conversation", key="marketing_reset"):
        reset_chat()

# Footer
st.divider()
st.caption("Bonne chance √† tous pour votre validation. üöÄ")
