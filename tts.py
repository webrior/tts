import streamlit as st
import streamlit.components.v1 as components
import edge_tts
import asyncio
import tempfile
from flask import Flask, Response

# ================= CONFIGURATION ADSENSE =================
ADSENSE_CLIENT = "ca-pub-1930140755399931"
ADSENSE_SLOT = "7259870550"  # ← Remplacez CE numéro par votre vrai slot AdSense !

# Script AdSense global
ADSENSE_SCRIPT = f"""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
     crossorigin="anonymous"></script>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({{
          google_ad_client: "{ADSENSE_CLIENT}",
          enable_page_level_ads: true
     }});
</script>
"""

# Balise meta de vérification
META_TAG = f"""
<meta name="google-adsense-account" content="{ADSENSE_CLIENT}">
"""

# ================= SERVEUR ADS.TXT =================
app = Flask(__name__)

@app.route('/ads.txt')
def serve_ads_txt():
    return Response(f"google.com, {ADSENSE_CLIENT}, DIRECT, f08c47fec0942fa0", mimetype='text/plain')

# ================= FONCTIONNALITÉS PRINCIPALES =================
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

# ================= INTERFACE UTILISATEUR =================
def main():
    # Injection AdSense
    components.html(META_TAG, height=0)
    components.html(ADSENSE_SCRIPT, height=0)
    
    # Bannière pub principale
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
    
    st.title("Text to Speech Converter")
    
    # Sélection de langue
    lang = st.selectbox("Language", options=list(LANGUAGES.keys()))
    lang_data = LANGUAGES[lang]
    
    # Choix de la voix
    voices = asyncio.run(get_voices(lang))
    voice_names = [v["Name"] for v in voices]
    selected_voice = st.selectbox(lang_data["select_voice"], voice_names)
    
    # Test de voix
    if st.button("Test Voice"):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            test_file = tmp_file.name
            asyncio.run(save_audio(lang_data["test_text"], selected_voice, test_file))
            st.audio(test_file)
            
            # Pub après test
            components.html(f"""
            <ins class="adsbygoogle"
                 style="display:block; text-align:center;"
                 data-ad-layout="in-article"
                 data-ad-format="fluid"
                 data-ad-client="{ADSENSE_CLIENT}"
                 data-ad-slot="{ADSENSE_SLOT}"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>
            """, height=200)
    
    # Zone de texte principale
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
                    
                    # Dernière pub
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
                    
                    if st.button("Generate another audio"):
                        st.experimental_rerun()

# ================= LANCEMENT =================
if __name__ == "__main__":
    # Lancement du serveur ads.txt
    from threading import Thread
    flask_thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080})
    flask_thread.daemon = True
    flask_thread.start()
    
    main()
