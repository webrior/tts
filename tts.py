import streamlit as st
import streamlit.components.v1 as components
import edge_tts
import asyncio
import tempfile
import os
from flask import Flask, Response
from threading import Thread
import pygame

# Initialisation pygame pour la lecture audio
pygame.mixer.init()

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

# Dictionnaire de langues (anglais, français, arabe)
LANGUAGES = {
    "english": {
        "title": "Text to Speech Pro",
        "select_voice": "Select Voice",
        "text_label": "Enter your text:",
        "generate": "Generate Audio",
        "success": "Audio generated successfully!",
        "test_text": "This is a test audio",
        "test_button": "Test Voice",
        "error_empty_text": "Please enter some text"
    },
    "french": {
        "title": "Synthèse Vocale Pro",
        "select_voice": "Choisir Voix",
        "text_label": "Entrez votre texte:",
        "generate": "Générer l'audio",
        "success": "Audio généré avec succès!",
        "test_text": "Ceci est un test audio",
        "test_button": "Tester la Voix",
        "error_empty_text": "Veuillez entrer du texte"
    },
    "arabic": {
        "title": "محول النص إلى كلام",
        "select_voice": "اختر صوتًا",
        "text_label": "أدخل النص الخاص بك:",
        "generate": "إنشاء الصوت",
        "success": "تم إنشاء الصوت بنجاح!",
        "test_text": "هذا اختبار صوتي",
        "test_button": "تجربة الصوت",
        "error_empty_text": "الرجاء إدخال نص"
    }
}

# Sélection de langue
language = st.selectbox("Language", options=list(LANGUAGES.keys()))
lang_data = LANGUAGES[language]

# Sélection de voix
async def get_voices(lang):
    voices = await edge_tts.VoicesManager.create()
    if lang == "french":
        return voices.find(Language="fr")
    elif lang == "arabic":
        return voices.find(Language="ar")
    else:
        return voices.find(Language="en")

voices = asyncio.run(get_voices(language))
voice_names = [v["Name"] for v in voices]
selected_voice = st.selectbox(lang_data["select_voice"], voice_names)

# Bouton de test de voix
if st.button(lang_data["test_button"]):
    test_text = lang_data["test_text"]
    with st.spinner("Playing test..."):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            communicate = edge_tts.Communicate(test_text, selected_voice)
            await communicate.save(tmp_file.name)
            pygame.mixer.music.load(tmp_file.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            os.unlink(tmp_file.name)

# Zone de texte
text = st.text_area(lang_data["text_label"], height=200)

# Bouton de génération
if st.button(lang_data["generate"]):
    if not text.strip():
        st.error(lang_data["error_empty_text"])
    else:
        with st.spinner("Generating audio..."):
            with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp_file:
                communicate = edge_tts.Communicate(text, selected_voice)
                await communicate.save(tmp_file.name)
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
