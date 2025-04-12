import streamlit as st
import streamlit.components.v1 as components
import edge_tts
import asyncio
import tempfile
import os
from flask import Flask, Response
from threading import Thread

# Configuration AdSense
ADSENSE_CLIENT = "ca-pub-1930140755399931"
ADSENSE_SLOT = "7259870550"  # ← Remplacez par votre vrai slot AdSense

# Meta Tag et Script AdSense
ADSENSE_HEAD = f"""
<meta name="google-adsense-account" content="{ADSENSE_CLIENT}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
    crossorigin="anonymous"></script>
"""

# Serveur Flask pour ads.txt
flask_app = Flask(__name__)

@flask_app.route('/ads.txt')
def serve_ads_txt():
    return Response("google.com, pub-1930140755399931, DIRECT, f08c47fec0942fa0", mimetype='text/plain')

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# Démarrer Flask dans un thread séparé
Thread(target=run_flask, daemon=True).start()

# Interface Streamlit
st.set_page_config(page_title="TTS Pro", layout="wide")

# Injection AdSense
components.html(ADSENSE_HEAD, height=0)
components.html(f"""
<ins class="adsbygoogle"
    style="display:block"
    data-ad-client="{ADSENSE_CLIENT}"
    data-ad-slot="{ADSENSE_SLOT}"
    data-ad-format="auto"
    data-full-width-responsive="true"></ins>
<script>
    (adsbygoogle = window.adsbygoogle || []).push({{}});
</script>
""", height=100)

# Fonctionnalités TTS
LANGUAGES = {
    "english": {
        "title": "Text to Speech Pro",
        "select_voice": "Select Voice",
        "text_label": "Enter your text:",
        "generate": "Generate Audio",
        "success": "Audio generated successfully!",
        "test_text": "This is a test audio"
    },
    "french": {
        "title": "Synthèse Vocale Pro",
        "select_voice": "Choisir Voix",
        "text_label": "Entrez votre texte:",
        "generate": "Générer l'audio",
        "success": "Audio généré avec succès!",
        "test_text": "Ceci est un test audio"
    }
}

# Sélection de langue
language = st.selectbox("Language", options=list(LANGUAGES.keys()))
lang_data = LANGUAGES[language]

# Sélection de voix
voices = asyncio.run(edge_tts.VoicesManager.create())
filtered_voices = voices.find(Language="fr" if language == "french" else "en")
voice_names = [v["Name"] for v in filtered_voices]
selected_voice = st.selectbox(lang_data["select_voice"], voice_names)

# Zone de texte
text = st.text_area(lang_data["text_label"], height=200)

# Boutons d'action
if st.button(lang_data["generate"]):
    if not text.strip():
        st.error(lang_data["error_empty_text"])
    else:
        with st.spinner("Generating audio..."):
            with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp_file:
                asyncio.run(edge_tts.Communicate(text, selected_voice).save(tmp_file.name))
                st.audio(tmp_file.name)
                st.success(lang_data["success"])

# Publicité en bas de page
components.html(f"""
<ins class="adsbygoogle"
    style="display:block"
    data-ad-client="{ADSENSE_CLIENT}"
    data-ad-slot="{ADSENSE_SLOT}"
    data-ad-format="auto"
    data-full-width-responsive="true"></ins>
<script>
    (adsbygoogle = window.adsbygoogle || []).push({{}});
</script>
""", height=100)
