import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

# Configuration minimale de pygame pour Render
import pygame
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.mixer.set_num_channels(8)

# Dictionnaire de langues simplifié
LANGUAGES = {
    "english": {
        "title": "Text to Speech",
        "select_voice": "Select Voice",
        "gender_label": "Gender:",
        "test_voice": "Test Voice",
        "text_label": "Enter your text:",
        "generate": "Generate Audio",
        "success": "Audio generated successfully!"
    },
    "french": {
        "title": "Synthèse Vocale",
        "select_voice": "Sélectionner une voix",
        "gender_label": "Genre:",
        "test_voice": "Tester la voix",
        "text_label": "Entrez votre texte:",
        "generate": "Générer l'audio",
        "success": "Audio généré avec succès!"
    },
    "arabic": {
        "title": "تحويل النص إلى كلام",
        "select_voice": "اختر صوتًا",
        "gender_label": "الجنس:",
        "test_voice": "اختبار الصوت",
        "text_label": "أدخل النص الخاص بك:",
        "generate": "إنشاء الصوت",
        "success": "تم إنشاء الصوت بنجاح!"
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

async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

async def test_voice(text, voice):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(temp_path)
        
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def main():
    st.title("Text to Speech App")
    
    # Sélection de langue
    lang = st.selectbox("Language", options=list(LANGUAGES.keys()))
    lang_data = LANGUAGES[lang]
    
    # Chargement des voix
    voices = asyncio.run(get_voices(lang))
    voice_names = [v["Name"] for v in voices]
    
    # Interface
    selected_voice = st.selectbox(lang_data["select_voice"], voice_names)
    gender = st.selectbox(lang_data["gender_label"], ["Male", "Female", "Both"])
    
    # Test de voix
    test_text = "This is a test" if lang == "english" else "Ceci est un test" if lang == "french" else "هذا اختبار"
    if st.button(lang_data["test_voice"]):
        asyncio.run(test_voice(test_text, selected_voice))
    
    # Génération d'audio
    text = st.text_area(lang_data["text_label"], height=200)
    
    if st.button(lang_data["generate"]):
        if not text.strip():
            st.error("Please enter some text")
        else:
            with st.spinner("Generating audio..."):
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                    asyncio.run(generate_audio(text, selected_voice, tmp_file.name))
                    st.audio(tmp_file.name)
                    st.success(lang_data["success"])

if __name__ == "__main__":
    main()
