import streamlit as st
import streamlit.components.v1 as components
import edge_tts
import asyncio
import tempfile
from flask import Flask, Response
from threading import Thread
import os

# ================= CONFIGURATION ADSENSE =================
ADSENSE_CLIENT = "ca-pub-1930140755399931"  # Votre ID AdSense
ADSENSE_SLOT = "7259870550"  # Remplacez par votre slot AdSense
ADS_TXT_CONTENT = "google.com, pub-1930140755399931, DIRECT, f08c47fec0942fa0"

# ================= SERVEUR FLASK POUR ADS.TXT =================
flask_app = Flask(__name__)

@flask_app.route('/ads.txt')
def serve_ads_txt():
    return Response(ADS_TXT_CONTENT, mimetype='text/plain')

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# ================= FONCTIONS PRINCIPALES =================
LANGUAGES = {
    "english": {
        "title": "Text to Speech",
        "select_voice": "Select Voice",
        "text_label": "Enter your text:",
        "generate": "Generate Audio",
        "success": "Audio generated successfully!",
        "test_text": "This is a test audio"
    },
    "french": {
        "title": "Synthèse Vocale",
        "select_voice": "Sélectionner une voix",
        "text_label": "Entrez votre texte:",
        "generate": "Générer l'audio",
        "success": "Audio généré avec succès!",
        "test_text": "Ceci est un test audio"
    }
}

async def get_voices(language):
    voices = await edge_tts.VoicesManager.create()
    return voices.find(Language="fr") if language == "french" else voices.find(Language="en")

async def save_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# ================= INTERFACE UTILISATEUR =================
def main():
    # Injection AdSense
    components.html(f"""
    <meta name="google-adsense-account" content="{ADSENSE_CLIENT}">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
        crossorigin="anonymous"></script>
    <ins class="adsbygoogle"
        style="display:block"
        data-ad-client="{ADSENSE_CLIENT}"
        data-ad-slot="{ADSENSE_SLOT}"
        data-ad-format="auto"
        data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    """, height=150)

    # Sélection de langue
    lang = st.selectbox("Language", options=list(LANGUAGES.keys()))
    lang_data = LANGUAGES[lang]

    # Chargement des voix
    voices = asyncio.run(get_voices(lang))
    selected_voice = st.selectbox(lang_data["select_voice"], [v["Name"] for v in voices])

    # Test de voix
    if st.button("Test Voice"):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            asyncio.run(save_audio(lang_data["test_text"], selected_voice, tmp_file.name))
            st.audio(tmp_file.name)

    # Génération d'audio principal
    text = st.text_area(lang_data["text_label"], height=200)
    
    if st.button(lang_data["generate"]):
        if not text.strip():
            st.error("Please enter some text")
        else:
            with st.spinner("Generating audio..."):
                with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp_file:
                    asyncio.run(save_audio(text, selected_voice, tmp_file.name))
                    st.audio(tmp_file.name)
                    st.success(lang_data["success"])

# ================= LANCEMENT =================
if __name__ == "__main__":
    # Démarrer Flask dans un thread séparé
    Thread(target=run_flask, daemon=True).start()
    
    # Configuration Streamlit
    st.set_page_config(page_title="Text-to-Speech", layout="wide")
    main()
