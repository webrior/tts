import streamlit as st
import streamlit.components.v1 as components
import edge_tts
import asyncio
import tempfile
import os
from flask import Flask, Response
from threading import Thread
from io import BytesIO

# ================= CONFIGURATION =================
ADSENSE_CLIENT = "ca-pub-1930140755399931"
ADSENSE_SLOT = "7259870550"  # À remplacer par votre slot

# ================= APPLICATION FLASK =================
flask_app = Flask(__name__, static_folder='static')

@flask_app.route('/ads.txt')
def serve_ads_txt():
    content = "google.com, pub-1930140755399931, DIRECT, f08c47fec0942fa0"
    return Response(content, mimetype='text/plain')

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# ================= DICTIONNAIRE DE LANGUES =================
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
        "download_ads": "Download ads.txt"
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
        "download_ads": "Télécharger ads.txt"
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
        "download_ads": "تنزيل ads.txt"
    }
}

# ================= FONCTIONS TTS =================
async def get_voices(lang):
    voices = await edge_tts.VoicesManager.create()
    if lang == "french":
        return voices.find(Language="fr")
    elif lang == "arabic":
        return voices.find(Language="ar")
    else:
        return voices.find(Language="en")

async def generate_audio(text, voice_name, filename="output.mp3"):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(filename)
    return filename

# ================= INTERFACE STREAMLIT =================
def main():
    st.set_page_config(page_title="TTS Pro", layout="wide")
    
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
    """, height=100)

    # Sélection de langue
    language = st.selectbox("Language", options=list(LANGUAGES.keys()))
    lang_data = LANGUAGES[language]

    # Sélection de voix
    voices = asyncio.run(get_voices(language))
    voice_names = [v["Name"] for v in voices]
    selected_voice = st.selectbox(lang_data["select_voice"], voice_names)

    # Zone de texte
    text = st.text_area(lang_data["text_label"], height=200)

    # Bouton de test
    if st.button(lang_data["test_button"]):
        if not text.strip():
            st.error(lang_data["error_empty_text"])
        else:
            with st.spinner("Generating test audio..."):
                test_file = asyncio.run(generate_audio(
                    lang_data["test_text"], 
                    selected_voice,
                    "test_audio.mp3"
                ))
                with open(test_file, "rb") as f:
                    st.download_button(
                        label="Download Test",
                        data=f,
                        file_name="test_audio.mp3",
                        mime="audio/mpeg"
                    )
                os.unlink(test_file)

    # Bouton de génération
    if st.button(lang_data["generate"]):
        if not text.strip():
            st.error(lang_data["error_empty_text"])
        else:
            with st.spinner("Generating audio..."):
                output_file = asyncio.run(generate_audio(text, selected_voice))
                with open(output_file, "rb") as f:
                    st.download_button(
                        label="Download Audio",
                        data=f,
                        file_name="generated_audio.mp3",
                        mime="audio/mpeg"
                    )
                st.success(lang_data["success"])
                os.unlink(output_file)

    # Téléchargement ads.txt alternatif
    st.markdown("---")
    ads_content = "google.com, pub-1930140755399931, DIRECT, f08c47fec0942fa0"
    st.download_button(
        label=lang_data["download_ads"],
        data=ads_content,
        file_name="ads.txt",
        mime="text/plain"
    )

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
    Thread(target=run_flask, daemon=True).start()
    
    # Démarrer Streamlit
    main()
