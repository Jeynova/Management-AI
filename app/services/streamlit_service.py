import os
import subprocess
import streamlit as st
from flask import redirect
from dotenv import load_dotenv

def streamlit_try():
    """Démarre Streamlit et redirige vers l'iframe."""
    streamlit_port = 8501
    streamlit_script = os.path.abspath("app\\assistant_data_analysis.py")
    print(streamlit_script)
    try:
        # Vérifiez si Streamlit est déjà en cours d'exécution
        subprocess.check_output(["pgrep", "-f", f"streamlit run {streamlit_script}"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        # Streamlit n'est pas en cours d'exécution, démarrez-le
        subprocess.Popen(["streamlit", "run", streamlit_script, "--server.port", str(streamlit_port)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Retourne simplement un succès
    return redirect(f"http://localhost:{streamlit_port}")