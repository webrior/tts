import streamlit as st
import os
import edge_tts
from edge_tts import VoicesManager
import asyncio
import tempfile
import pygame
from mutagen.mp3 import MP3
import shutil

# Dictionnaire de Langues
LANGUAGES = {
    "english": {
        "title": "Content Creator TTS",
        "keywords_label": "Search Keywords:",
        "total_duration_label": "Total Video Duration (seconds):",
        "clip_duration_label": "Clip Duration (seconds):",
        "choose_folder": "Choose Save Directory",
        "search_download": "Search and Download",
        "preview": "Ready to go",
        "error": "Error",
        "error_empty_text": "No text found for voice over.",
        "please_select_a_voice": "please select a voice",
        'pexels_api_error': 'Please check your Pexels API',
        'pixabay_api_error': 'Please check your Pixabay API',
        "success": "Success",
        "warning": "Warning",
        "choose_folder_msg": "The save folder is:\n",
        "no_keywords": "Please enter search keywords.",
        "download_complete": "Download and video creation completed.",
        "no_videos": "No videos found for your keyword.",
        "platform_label": "Orientation:",
        "no_videos_resized": "No videos resized successfully.",
        "select_folder": "Select a folder to merge videos",
        "text_label": "Text:",
        "gender voice error": "Selected voice does not match the specified gender.",
        "tts_label": "TTS:",
        "choose_folder": "Choose Folder",
        "search_download": "Generate voice over",
        "preview": "Preview",
        "text_label": "Enter your text:",
        "tts_language_label": "TTS Language:",
        "stop": "Stop",
        "license_label": "License",
        "voice_test": "Test Voice",
        "select_voice": "Select Voice",
        "gender_label": "Gender:",
        "test_voice": "Test Voice",
        "tts_language_label": "TTS Language:",
        "merge_videos": "Merging Videos...",
        "Processing final video": "Processing videos...",
        "downloading_video": "processing...",
        "stop": "Stop",
        "merge_videos_audio": "merging video with audio...",
        "not_enough_videos": "not enough videos!",
        "api_button": "APIs Keys",
        "pixabay_label": "PIXABAY API Key:",
        "pexels_label": "PEXELS API Key:",
        "license_label": "License Key",
        "missing_api_keys": "Please ensure both PIXABAY and PEXELS API keys are set.",
        "success": "Success",
        'error': 'Error',
        "license_not_found": "License not found",
        'failed_to_connect_to_airtable': "impossible de se connecter a airtable",
        "mac_added": "MAC address added successfully",
        "database updated": "database updated",
        "error updating data base": "error updating data base",
        "stopped": "stopped",
    },
    "french": {
        "title": "Content Creator TTS",
        "keywords_label": "Mots-clés de recherche :",
        "total_duration_label": "Durée totale de la vidéo (secondes) :",
        "clip_duration_label": "Durée de chaque clip (secondes) :",
        "choose_folder": "Choisir le dossier de sauvegarde",
        "search_download": "Rechercher et Télécharger",
        "preview": "prêt",
        "error": "Erreur",
        "please_select_a_voice": "veuillez sélectionner une voix",
        'pexels_api_error': 'Veuillez vérifier votre API Pexels',
        'pixabay_api_error': 'Veuillez vérifier votre API Pixabay',
        "success": "Succès",
        "choose_folder": "Choisir Dossier",
        "search_download": "Générer une voix off",
        "preview": "Aperçu",
        "text_label": "Entrez votre texte:",
        "tts_language_label": "Langue TTS:",
        "stop": "Arrêter",
        "error_empty_text": "Aucun texte trouvé pour la voix off.",
        "license_label": "Licence",
        "voice_test": "Tester la Voix",
        "select_voice": "Choisir Voix",
        "gender_label": "Genre:",
        "warning": "Avertissement",
        "choose_folder_msg": "Le dossier de sauvegarde est :\n",
        "no_keywords": "Veuillez entrer des mots-clés de recherche.",
        "download_complete": "Téléchargement et création de la vidéo terminés.",
        "no_videos": "Aucune vidéo trouvée pour votre mot-clé.",
        "platform_label": "Orientation :",
        "no_videos_resized": "Aucune vidéo redimensionnée avec succès.",
        "select_folder": "Sélectionnez un dossier pour fusionner les vidéos",
        "text_label": "Texte :",
        "tts_label": "TTS :",
        "test_voice": "Test de la voix",
        "gender voice error": "Voix sélectionnée ne correspond pas au genre spécifié.",
        "tts_language_label": "Langue du TTS :",
        "merge_videos": "Fusionnement des vidéos...",
        "stop": "Arrêter",
        "downloading_video": "processing...",
        "merge_videos_audio": "Implémentation de l'audio avec la vidéo...",
        "Processing final video...": "Traitement des vidéos...",
        "not_enough_videos": "Pas assez de vidéos !",
        "api_button": "APIs",
        "pixabay_label": "Clé API de PIXABAY :",
        "pexels_label": "Clé API de PEXELS :",
        "license_label": "Clé de Licence",
        "missing_api_keys": "Veuillez vous assurer que les clés API de PIXABAY et PEXELS sont définies.",
        "license_not_found": "Licence non trouvée",
        "failed_to_connect_to_airtable": "Impossible de se connecter à Airtable",
        "mac_added": "Adresse MAC ajoutée avec succès",
        "database_updated": "Base de données mise à jour",
        "error_updating_database": "Erreur lors de la mise à jour de la base de données",
        "stopped": "stopé",
    },
    "arabic": {
        "title": "Content Creator TTS",
        "keywords_label": "كلمات البحث:",
        "total_duration_label": "مدة الفيديو الإجمالية (بالثواني):",
        "clip_duration_label": "مدة كل مقطع (بالثواني):",
        "choose_folder": "اختر دليل الحفظ",
        "search_download": "بحث وتحميل",
        "preview": "مستعد",
        "license_not_found": "يرجى اختيار صوت",
        "error": "خطأ",
        'pexels_api_error': 'يرجى التحقق من واجهة برمجة تطبيقات Pexels الخاصة بك',
        'pixabay_api_error': 'يرجى التحقق من واجهة برمجة تطبيقات Pixabay الخاصة بك',
        "success": "نجاح",
        "warning": "تحذير",
        "choose_folder_msg": "دليل الحفظ هو:\n",
        "no_keywords": "يرجى إدخال كلمات البحث.",
        "download_complete": "اكتمل التحميل وإنشاء الفيديو.",
        "no_videos": "لم يتم العثور على مقاطع فيديو للكلمة الرئيسية الخاصة بك.",
        "platform_label": "نوع الفيديو:",
        "no_videos_resized": "لم يتم إعادة تحجيم أي فيديو بنجاح.",
        "select_folder": "اختر مجلدًا لدمج الفيديوهات",
        "text_label": "النص:",
        "tts_label": "TTS:",
        "error_empty_text": "لم يتم العثور على نص للتعليق الصوتي.",
        "test_voice": "تجربة الصوت",
        "gender voice error": "الصوت المحدد لا يتطابق مع الجنس المحدد.",
        "tts_language_label": "لغة TTS:",
        "merge_videos": "دمج الفيديوهات...",
        "stop": "إيقاف",
        "downloading_video": "processing...",
        "merge_videos_audio": "تنفيذ الصوت مع الفيديو...",
        "Processing final video...": "معالجة الفيديوهات...",
        "not_enough_videos": "لا يوجد مقاطع فيديو كافية!",
        "api_button": "APIs",
        "pixabay_label": "مفتاح PIXABAY API:",
        "pexels_label": "مفتاح PEXELS API:",
        "license_label": "مفتاح الترخيص",
        "missing_api_keys": "يرجى التأكد من تعيين مفاتيح API لكل من PIXABAY و PEXELS.",
        "license_not_found": "لم يتم العثور على الترخيص",
        "failed_to_connect_to_airtable": "تعذر الاتصال بـ Airtable",
        "mac_added": "تمت إضافة عنوان MAC بنجاح",
        "database_updated": "تم تحديث قاعدة البيانات",
        "choose_folder": "اختر المجلد",
        "search_download": "إنشاء تعليق صوتي",
        "preview": "معاينة",
        "text_label": "أدخل النص الخاص بك:",
        "tts_language_label": "لغة TTS:",
        "stop": "إيقاف",
        "license_label": "الرخصة",
        "voice_test": "اختبار الصوت",
        "select_voice": "اختر الصوت",
        "gender_label": "النوع:",
        "error_updating_database": "خطأ أثناء تحديث قاعدة البيانات",
        "stopped": "توقف",
    }
}

# Initialiser pygame pour la lecture audio
pygame.mixer.init()

class TTSApp:
    def __init__(self):
        self.current_language = "english"
        self.save_directory = ""
        self.stop_event = False
        self.voices = []
        
        # Initialiser l'état de Streamlit
        if 'language' not in st.session_state:
            st.session_state.language = "english"
        if 'voices_loaded' not in st.session_state:
            st.session_state.voices_loaded = False
        
        self.setup_ui()
    
    def setup_ui(self):
        st.title("Content Creator TTS")
        
        # Sélecteur de langue
        self.current_language = st.selectbox(
            "Language:",
            options=list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.language),
            key="language_select"
        )
        st.session_state.language = self.current_language
        current_lang_data = LANGUAGES[self.current_language]
        
        # Sélecteur de langue TTS
        tts_language = st.selectbox(
            current_lang_data["tts_language_label"],
            options=["english", "french", "arabic"],
            key="tts_language"
        )
        
        # Charger les voix disponibles pour la langue sélectionnée
        if not st.session_state.voices_loaded or 'tts_language' in st.session_state and st.session_state.tts_language != tts_language:
            self.load_voices(tts_language)
            st.session_state.tts_language = tts_language
            st.session_state.voices_loaded = True
        
        # Sélecteur de voix
        if self.voices:
            voice_names = [v["Name"] for v in self.voices]
            selected_voice = st.selectbox(
                current_lang_data["select_voice"],
                options=voice_names,
                key="voice_select"
            )
        else:
            st.warning(current_lang_data["please_select_a_voice"])
        
        # Sélecteur de genre
        gender = st.selectbox(
            current_lang_data["gender_label"],
            options=["Male", "Female", "Both"],
            key="gender_select"
        )
        
        # Bouton de test de voix
        if st.button(current_lang_data["test_voice"]):
            self.test_voice(tts_language, st.session_state.voice_select, gender)
        
        # Zone de texte
        text_content = st.text_area(
            current_lang_data["text_label"],
            height=200,
            key="text_content"
        )
        
        # Sélecteur de dossier de sauvegarde
        if st.button(current_lang_data["choose_folder"]):
            self.choose_save_directory()
        
        if self.save_directory:
            st.info(f"{current_lang_data['choose_folder_msg']} {self.save_directory}")
        
        # Bouton de génération
        if st.button(current_lang_data["search_download"]):
            if not text_content.strip():
                st.error(current_lang_data["error_empty_text"])
            elif not hasattr(st.session_state, 'voice_select') or st.session_state.voice_select == "Select Voice":
                st.error(current_lang_data["please_select_a_voice"])
            else:
                self.generate_audio(
                    text_content,
                    tts_language,
                    st.session_state.voice_select,
                    gender
                )
    
    async def load_voices_async(self, language):
        voices = await VoicesManager.create()
        if language == "french":
            return voices.find(Language="fr")
        elif language == "arabic":
            return voices.find(Language="ar")
        elif language == "english":
            return voices.find(Language="en")
        return []
    
    def load_voices(self, language):
        self.voices = asyncio.run(self.load_voices_async(language))
    
    def choose_save_directory(self):
        # Dans Streamlit, on ne peut pas ouvrir un sélecteur de dossier natif
        # On utilise un champ de texte pour entrer le chemin manuellement
        folder_path = st.text_input("Enter the save directory path:")
        if folder_path and os.path.isdir(folder_path):
            self.save_directory = folder_path
            st.success(f"Save directory set to: {self.save_directory}")
        else:
            st.error("Invalid directory path")
    
    async def generate_audio_async(self, text, language, voice_name, gender):
        if not self.save_directory:
            st.error(LANGUAGES[self.current_language]["choose_folder_msg"])
            return
        
        final_video_directory = os.path.join(self.save_directory, "Output Voice_over")
        os.makedirs(final_video_directory, exist_ok=True)
        output_file = os.path.join(final_video_directory, "Voice.MP3")
        
        # Vérifier que la voix correspond au genre sélectionné
        selected_voice = next((v for v in self.voices if v["Name"] == voice_name), None)
        if not selected_voice:
            st.error(LANGUAGES[self.current_language]["please_select_a_voice"])
            return
        
        if gender != "Both" and selected_voice["Gender"] != gender:
            st.error(LANGUAGES[self.current_language]["gender voice error"])
            return
        
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_file)
        
        st.success(LANGUAGES[self.current_language]["success"])
        st.audio(output_file)
    
    def generate_audio(self, text, language, voice_name, gender):
        asyncio.run(self.generate_audio_async(text, language, voice_name, gender))
    
    async def test_voice_async(self, language, voice_name, gender):
        # Déterminer le texte de test en fonction de la langue
        text = "This is a test" if language == "english" else "Ceci est un test" if language == "french" else "هذا اختبار"
        
        # Vérifier que la voix correspond au genre sélectionné
        selected_voice = next((v for v in self.voices if v["Name"] == voice_name), None)
        if not selected_voice:
            st.error(LANGUAGES[self.current_language]["please_select_a_voice"])
            return
        
        if gender != "Both" and selected_voice["Gender"] != gender:
            st.error(LANGUAGES[self.current_language]["gender voice error"])
            return
        
        communicate = edge_tts.Communicate(text, voice_name)
        
        # Créer un fichier temporaire pour l'audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            await communicate.save(temp_file_path)
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            # Attendre la fin de la lecture
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        finally:
            try:
                os.remove(temp_file_path)
            except:
                pass
    
    def test_voice(self, language, voice_name, gender):
        asyncio.run(self.test_voice_async(language, voice_name, gender))

# Lancer l'application
if __name__ == "__main__":
    app = TTSApp()
