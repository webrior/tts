import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

# Configuration spéciale pour Render - Pas besoin de pygame.mixer.init()
# Nous utiliserons directement la lecture audio de Streamlit

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
    },
    "arabic": {
        "title": "تحويل النص إلى كلام",
        "select_voice": "اختر صوتًا",
        "text_label": "أدخل النص الخاص بك:",
        "generate": "إنشاء الصوت",
        "success": "تم إنشاء الصوت بنجاح!",
        "test_text": "هذا اختبار صوتي"
    }
}

async def get_voices(language):
    voices = await edge_tts.VoicesManager.create()
    if language == "french":
        return voices.find(Language="fr")
    elif language == "arabic":
        return voices.find(Language="ar")
    else:
        return voices.find(Language="en")

async def save_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def main():
    st.title("Text to Speech Converter")
    
    # Sélection de langue
    lang = st.selectbox("Language", options=list(LANGUAGES.keys()))
    lang_data = LANGUAGES[lang]
    
    # Chargement des voix
    voices = asyncio.run(get_voices(lang))
    voice_names = [v["Name"] for v in voices]
    selected_voice = st.selectbox(lang_data["select_voice"], voice_names)
    
    # Test de voix
    if st.button("Test Voice"):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            test_file = tmp_file.name
            asyncio.run(save_audio(lang_data["test_text"], selected_voice, test_file))
            st.audio(test_file)
    
    # Génération d'audio principal
    text = st.text_area(lang_data["text_label"], height=200)
    
    if st.button(lang_data["generate"]):
        if not text.strip():
            st.error("Please enter some text")
        else:
            with st.spinner("Generating audio..."):
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                    asyncio.run(save_audio(text, selected_voice, tmp_file.name))
                    st.audio(tmp_file.name)
                    st.success(lang_data["success"])

if __name__ == "__main__":
    main()
