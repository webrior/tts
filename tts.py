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
ADSENSE_SLOT = "7259870550"  # Remplacez par votre vrai slot AdSense

# Application Flask
flask_app = Flask(__name__)

@flask_app.route('/ads.txt')
def serve_ads_txt():
    return Response("google.com, pub-1930140755399931, DIRECT, f08c47fec0942fa0", mimetype='text/plain')

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# Dictionnaire de langues
LANGUAGES = {
    "english": {
        "title": "Text to Speech Pro",
        "select_voice": "Select Voice",
        "text_label": "Enter your text:",
        "generate": "Generate Audio",
        "success": "Audio generated successfully!",
        "test_text": "This is a test audio",
        "test_button": "Test Voice",
        "error_empty_text": "Please enter some text",
        "audio_warning": "Audio preview available in download"
    },
    "french": {
        "title": "Synthèse Vocale Pro",
        "select_voice": "Choisir Voix",
        "text_label": "Entrez votre texte:",
        "generate": "Générer l'audio",
        "success": "Audio généré avec succès!",
        "test_text": "Ceci est un test audio",
        "test_button": "Tester la Voix",
        "error_empty_text": "Veuillez entrer du texte",
        "audio_warning": "Aperçu audio disponible en téléchargement"
    },
    "arabic": {
        "title": "محول النص إلى كلام",
        "select_voice": "اختر صوتًا",
        "text_label": "أدخل النص الخاص بك:",
        "generate": "إنشاء الصوت",
        "success": "تم إنشاء الصوت بنجاح!",
        "test_text": "هذا اختبار صوتي",
        "test_button": "تجربة الصوت",
        "error_empty_text": "الرجاء إدخال نص",
        "audio_warning": "معاينة الصوت متاحة في التنزيل"
    }
}

# Fonctions asynchrones
async def get_voices(lang):
    voices = await edge_tts.VoicesManager.create()
    if lang == "french":
        return voices.find(Language="fr")
    elif lang == "arabic":
        return voices.find(Language="ar")
    else:
        return voices.find(Language="en")

async def generate_audio_file(text, voice_name, file_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(file_path)

# Interface Streamlit
def main():
    st.set_page_config(page_title="TTS Pro", layout="wide")
    
    # Injection AdSense
    components.html(f"""<meta name="google-adsense-account" content="{ADSENSE_CLIENT}">""", height=0)
    components.html(f"""
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
        crossorigin="anonymous"></script>
    <ins class="adsbygoogle"
        style="display:block"
        data-ad-client="{ADSENSE_CLIENT}"
        data-ad-slot="{ADSENSE_SLOT}"
        data-ad-format="auto"
        data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    """, height=100)

    # Sélection de langue
    language = st.selectbox("Language", options=list(LANGUAGES.keys()))
    lang_data = LANGUAGES[language]

    # Sélection de voix
    voices = asyncio.run(get_voices(language))
    voice_names = [v["Name"] for v in voices]
    selected_voice = st.selectbox(lang_data["select_voice"], voice_names)

    # Bouton de test de voix (version alternative sans lecture)
    if st.button(lang_data["test_button"]):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            test_text = lang_data["test_text"]
            asyncio.run(generate_audio_file(test_text, selected_voice, tmp_file.name))
            with open(tmp_file.name, "rb") as f:
                st.download_button(
                    label="Download Test Audio",
                    data=f,
                    file_name="test_audio.mp3",
                    mime="audio/mpeg"
                )
            st.warning(lang_data["audio_warning"])
            os.unlink(tmp_file.name)

    # Zone de texte
    text = st.text_area(lang_data["text_label"], height=200)

    # Bouton de génération
    if st.button(lang_data["generate"]):
        if not text.strip():
            st.error(lang_data["error_empty_text"])
        else:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                asyncio.run(generate_audio_file(text, selected_voice, tmp_file.name))
                with open(tmp_file.name, "rb") as f:
                    st.download_button(
                        label="Download Audio",
                        data=f,
                        file_name="generated_audio.mp3",
                        mime="audio/mpeg"
                    )
                st.success(lang_data["success"])
                os.unlink(tmp_file.name)

    # Publicité en bas de page
    components.html(f"""
    <ins class="adsbygoogle"
        style="display:block"
        data-ad-client="{ADSENSE_CLIENT}"
        data-ad-slot="{ADSENSE_SLOT}"
        data-ad-format="auto"
        data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    """, height=100)

if __name__ == "__main__":
    # Démarrer Flask dans un thread séparé
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Démarrer Streamlit
    main()
