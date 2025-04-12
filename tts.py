import tkinter as tk
from tkinter import font, messagebox, filedialog
import edge_tts
from edge_tts import VoicesManager
import asyncio
import tempfile
import pygame
import os
from flask import Flask, Response
from threading import Thread
import threading

# Configuration AdSense
ADSENSE_CLIENT = "ca-pub-1930140755399931"
ADSENSE_SLOT = "7259870550"  # Remplacez par votre slot AdSense
ADSENSE_CODE = f"""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
    crossorigin="anonymous"></script>
<script>
    (adsbygoogle = window.adsbygoogle || []).push({{
        google_ad_client: "{ADSENSE_CLIENT}",
        enable_page_level_ads: true
    }});
</script>
"""

# Dictionnaire de Langues (version simplifiée)
LANGUAGES = {
    "english": {
        "title": "Text to Speech Pro",
        "select_voice": "Select Voice",
        "text_label": "Enter your text:",
        "generate": "Generate Audio",
        "success": "Audio generated successfully!",
        "test_text": "This is a test audio",
        "choose_folder": "Choose Save Directory",
        "voice_test": "Test Voice",
        "tts_language_label": "TTS Language:",
        "gender_label": "Gender:",
        "error_empty_text": "Please enter some text"
    },
    "french": {
        "title": "Synthèse Vocale Pro",
        "select_voice": "Choisir Voix",
        "text_label": "Entrez votre texte:",
        "generate": "Générer l'audio",
        "success": "Audio généré avec succès!",
        "test_text": "Ceci est un test audio",
        "choose_folder": "Choisir Dossier",
        "voice_test": "Tester la Voix",
        "tts_language_label": "Langue TTS:",
        "gender_label": "Genre:",
        "error_empty_text": "Veuillez entrer du texte"
    },
    "arabic": {
        "title": "محول النص إلى كلام",
        "select_voice": "اختر صوتًا",
        "text_label": "أدخل النص الخاص بك:",
        "generate": "إنشاء الصوت",
        "success": "تم إنشاء الصوت بنجاح!",
        "test_text": "هذا اختبار صوتي",
        "choose_folder": "اختر المجلد",
        "voice_test": "تجربة الصوت",
        "tts_language_label": "لغة TTS:",
        "gender_label": "النوع:",
        "error_empty_text": "الرجاء إدخال نص"
    }
}

# Serveur Flask pour ads.txt
flask_app = Flask(__name__)

@flask_app.route('/ads.txt')
def serve_ads_txt():
    return Response("google.com, pub-1930140755399931, DIRECT, f08c47fec0942fa0", mimetype='text/plain')

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        pygame.mixer.init()
        self.current_audio_file = None
        self.stop_event = threading.Event()
        
        # Démarrer Flask dans un thread séparé
        Thread(target=run_flask, daemon=True).start()

    def setup_ui(self):
        self.root.title("Text to Speech Pro")
        self.root.geometry("900x700")
        
        # AdSense Integration Frame
        self.adsense_frame = tk.Frame(self.root, height=100, bg="white")
        self.adsense_frame.pack(fill=tk.X, pady=5)
        tk.Label(self.adsense_frame, text="AdSense", bg="white").pack()
        
        # Main Content Frame
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Language Selection
        self.language_var = tk.StringVar(value="english")
        tk.Label(content_frame, text="Language:").grid(row=0, column=0, padx=10, pady=10)
        tk.OptionMenu(content_frame, self.language_var, *LANGUAGES.keys(), command=self.update_language).grid(row=0, column=1, padx=10, pady=10)

        # TTS Settings
        self.tts_language_var = tk.StringVar(value="english")
        tk.Label(content_frame, text=self.current_language["tts_language_label"]).grid(row=1, column=0, padx=10, pady=10)
        tk.OptionMenu(content_frame, self.tts_language_var, "english", "french", "arabic", command=self.update_voice_options).grid(row=1, column=1, padx=10, pady=10)

        # Gender Selection
        self.gender_var = tk.StringVar(value="Both")
        tk.Label(content_frame, text=self.current_language["gender_label"]).grid(row=2, column=0, padx=10, pady=10)
        tk.OptionMenu(content_frame, self.gender_var, "Male", "Female", "Both").grid(row=2, column=1, padx=10, pady=10)

        # Voice Selection
        self.voice_var = tk.StringVar()
        self.voice_menu = tk.OptionMenu(content_frame, self.voice_var, "Select Voice")
        self.voice_menu.grid(row=3, column=1, padx=10, pady=10)
        self.update_voice_options("english")

        # Test Button
        tk.Button(content_frame, text=self.current_language["voice_test"], command=self.test_voice).grid(row=3, column=2, padx=10, pady=10)

        # Text Entry
        tk.Label(content_frame, text=self.current_language["text_label"]).grid(row=4, column=0, padx=10, pady=10)
        self.text_entry = tk.Text(content_frame, height=15, width=70)
        self.text_entry.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        # Action Buttons
        tk.Button(content_frame, text=self.current_language["choose_folder"], command=self.choose_directory).grid(row=6, column=0, padx=10, pady=10)
        tk.Button(content_frame, text=self.current_language["generate"], command=self.generate_audio).grid(row=6, column=1, padx=10, pady=10)

        # Status Label
        self.status_label = tk.Label(content_frame, text="", fg="blue")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)

        # Bottom AdSense Frame
        bottom_ads_frame = tk.Frame(self.root, height=100, bg="white")
        bottom_ads_frame.pack(fill=tk.X, pady=5)
        tk.Label(bottom_ads_frame, text="AdSense", bg="white").pack()

    @property
    def current_language(self):
        return LANGUAGES[self.language_var.get()]

    def update_language(self, _):
        self.root.title(self.current_language["title"])
        # Update other UI elements as needed

    async def update_voice_options(self, language):
        voices = await VoicesManager.create()
        if language == "french":
            available_voices = voices.find(Language="fr")
        elif language == "arabic":
            available_voices = voices.find(Language="ar")
        else:
            available_voices = voices.find(Language="en")
        
        menu = self.voice_menu["menu"]
        menu.delete(0, "end")
        
        for voice in available_voices:
            menu.add_command(label=voice["Name"], 
                           command=lambda v=voice["Name"]: self.voice_var.set(v))

    def choose_directory(self):
        self.save_directory = filedialog.askdirectory()
        if self.save_directory:
            messagebox.showinfo("Info", f"Audio will be saved to: {self.save_directory}")

    def test_voice(self):
        if not self.voice_var.get() or self.voice_var.get() == "Select Voice":
            messagebox.showwarning("Warning", "Please select a voice first")
            return
            
        text = self.current_language["test_text"]
        asyncio.run(self._test_voice(text, self.voice_var.get()))

    async def _test_voice(self, text, voice_name):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(tmp_file.name)
            
            pygame.mixer.music.load(tmp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            os.unlink(tmp_file.name)

    def generate_audio(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", self.current_language["error_empty_text"])
            return
            
        if not hasattr(self, 'save_directory'):
            messagebox.showerror("Error", "Please select a save directory first")
            return
            
        voice_name = self.voice_var.get()
        if not voice_name or voice_name == "Select Voice":
            messagebox.showerror("Error", "Please select a voice first")
            return
            
        output_file = os.path.join(self.save_directory, "output.mp3")
        asyncio.run(self._generate_audio(text, voice_name, output_file))
        messagebox.showinfo("Success", self.current_language["success"])

    async def _generate_audio(self, text, voice_name, output_path):
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
