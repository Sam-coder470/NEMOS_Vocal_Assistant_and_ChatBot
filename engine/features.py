from playsound import playsound
import json
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import pvporcupine
import pyaudio
import pyautogui
import struct
import time
import os
import eel
import re
import difflib
import threading
import webbrowser
import subprocess
from huggingface_hub import InferenceClient
from hugchat import hugchat
from hugchat.login import Login
import pywhatkit as kit
from engine.config import*
from engine.command import*
from engine.database import get_from_db, save_to_db

# Fonction permettant de jouer le son d'ouverture de N.E.M.O.S sans bloquer l'exécution
@eel.expose
def playAssistantSound():
   music_dir = "C:\\Users\\User\\Desktop\\N.E.M.O.S\\N.E.M.O.S\\N.E.M.O.S\\www\\assets\\audio\\son_ouverture.mp3"
   threading.Thread(target=playsound, args=(music_dir,), daemon=True).start()

# Debut fonction pour la lecture de videos sur youtube

def extract_yt_term(command):
    """Extrait le titre de la vidéo YouTube et applique des filtres intelligents."""
    command = command.lower().strip()
    command = re.sub(r"^(mets|joue|lance|play)\s+", "", command)  # Supprime "mets ", "joue ", etc.
    command = command.replace(" sur youtube", "").replace(" on youtube", "").strip()  # Supprime "sur YouTube"

    # Filtres intelligents pour améliorer la recherche
    if "musique" in command or "chanson" in command:
        command += " lyrics officiel"
    elif "courte" in command:
        command += " short"
    elif "live" in command:
        command += " live"
    elif "documentaire" in command or "doc" in command:
        command += " documentaire"
    elif "cours" in command or "formation" in command or "apprendre" in command:
        command += " tutoriel cours complet"
    elif "informatif" in command or "explication" in command:
        command += " vidéo éducative explication"
    return command if command else None

def PlayYoutube(query):
    """Joue une vidéo YouTube en fonction de la requête utilisateur."""
    search_term = extract_yt_term(query)

    if search_term:
        speak(f"Recherche et lecture de {search_term} sur YouTube...")

        # Ouvre les résultats YouTube avant de jouer la vidéo
        url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
        webbrowser.open(url)

        try:
            kit.playonyt(search_term)
        except Exception as e:
            speak("Désolé, une erreur est survenue en lançant la vidéo.")
            print(f"⚠️ Erreur : {e}")
    else:
        speak("Je n'ai pas compris quelle vidéo jouer. Pouvez-vous reformuler ?")
#Fin fonction pour la lecture sur youtube
# Debut fonction pour le lancement des applications
       # Fonction pour vérifier si une application est installée en utilisant son chemin
def is_installed(app_path):
    """Vérifie si l'application est installée en utilisant le chemin donné."""
    return os.path.exists(app_path)

       # Recherche le chemin d'une application en utilisant la commande 'where' (Windows)
def find_app_path(query):
    """Recherche le chemin d'une application en utilisant 'where' (Windows)."""
    try:
        result = subprocess.run(["where", query], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]  # Retourne le premier chemin trouvé
        else:
            return None
    except Exception as e:
        print(f"Erreur lors de la recherche de l'application: {e}")
        return None
 
def openCommand(query):
    """Ouvre une application avec une meilleure précision et tolérance aux erreurs."""
    
    # Normalisation de la requête pour une meilleure comparaison
    query = query.lower().strip()
    query = re.sub(r"^(ouvre|lance)\s+", "", query)  # Supprime "ouvre " ou "lance "
    
    # Dictionnaire des applications courantes avec leurs alias (versions multiples)
    app_paths = {
        "chrome": ["chrome", "google chrome", "navigator"],
        "word": ["word", "microsoft word", "office word"],
        "excel": ["excel", "microsoft excel", "office excel"],
        "vlc": ["vlc", "video lan", "player"],
        "bloc-notes": ["bloc-notes", "notepad", "éditeur de texte"],
        "calculatrice": ["calculatrice", "calc"],
        "explorateur": ["explorateur", "explorer", "gestionnaire de fichiers"],
        "commande": ["invite de commande", "cmd", "terminal"]
    }

    # Recherche d'un alias correspondant à la requête
    app_to_launch = None
    for app, aliases in app_paths.items():
        if any(alias in query for alias in aliases):
            app_to_launch = app
            break

    if app_to_launch:
        app_path = app_paths[app_to_launch][0]  # Prendre le premier alias comme chemin par défaut

        # Chemins des applications
        app_path_map = {
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "bloc-notes": "C:\\Windows\\notepad.exe",
            "calculatrice": "C:\\Windows\\System32\\calc.exe",
            "explorateur": "C:\\Windows\\explorer.exe",
            "commande": "C:\\Windows\\System32\\cmd.exe"
        }

        # Vérification si l'application est installée
        if is_installed(app_path_map[app_to_launch]):
            speak(f"Ouverture de {app_to_launch}")
            os.startfile(app_path_map[app_to_launch])
        else:
            speak(f"L'application {app_to_launch} n'est pas installée.")
    else:
        # Recherche de l'application via 'where' (commande système Windows)
        app_path = find_app_path(query)
        if app_path:
            speak(f"Ouverture de {query}")
            os.startfile(app_path)
        else:
            speak("Je ne trouve pas cette application. Voulez-vous que je recherche sur Internet ?")
            
# Fin de la fonction de lancement des applications

#Debut fonction pour ouverture des sites webs 

def openWebsite(query):
    """Ouvre un site web à partir d'une requête utilisateur, avec plusieurs variations d'entrées."""
    
    # Convertir la requête en minuscule et nettoyer les espaces
    query = query.lower().strip()
    
    # Mappage des sites courants
    site_map = {
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "tiktok": "https://www.tiktok.com",
            "youtube": "https://www.youtube.com",
            "whatsapp": "https://www.whatsapp.com",
            "snapchat": "https://www.snapchat.com",
            "pinterest": "https://www.pinterest.com",
            "reddit": "https://www.reddit.com",
            "tumblr": "https://www.tumblr.com",
            "l'école supérieure de technologie d'agadir": "https://www.ecours.esta.ac.ma",
        
            "google": "https://www.google.com",
            "bing": "https://www.bing.com",
            "yahoo": "https://www.yahoo.com",
            "duckduckgo": "https://www.duckduckgo.com",
        
            "wikipedia": "https://www.wikipedia.org",
            "wiktionary": "https://www.wiktionary.org",
            "wikidata": "https://www.wikidata.org",
        
            "gmail": "https://mail.google.com",
            "outlook": "https://outlook.live.com",
            "yahoo mail": "https://mail.yahoo.com",
            "protonmail": "https://protonmail.com",
        
            "youtube music": "https://music.youtube.com",
            "spotify": "https://www.spotify.com",
            "soundcloud": "https://www.soundcloud.com",
            "apple music": "https://www.apple.com/music/",
        
            "google maps": "https://maps.google.com",
            "openstreetmap": "https://www.openstreetmap.org",
            
            "amazon": "https://www.amazon.com",
            "ebay": "https://www.ebay.com",
            "aliexpress": "https://www.aliexpress.com",
            "etsy": "https://www.etsy.com",
            "walmart": "https://www.walmart.com",
            
            "netflix": "https://www.netflix.com",
            "disney+": "https://www.disneyplus.com",
            "hulu": "https://www.hulu.com",
            "prime video": "https://www.primevideo.com",
            
            "bbc": "https://www.bbc.com",
            "cnn": "https://www.cnn.com",
            "nytimes": "https://www.nytimes.com",
            "le monde": "https://www.lemonde.fr",
            "the guardian": "https://www.theguardian.com",
            
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "gitlab": "https://www.gitlab.com",
            
            "w3schools": "https://www.w3schools.com",
            "geeksforgeeks": "https://www.geeksforgeeks.org",
            "mdn web docs": "https://developer.mozilla.org",
            
            "imdb": "https://www.imdb.com",
            "rottentomatoes": "https://www.rottentomatoes.com",
            "letterboxd": "https://letterboxd.com",
            
            "weather": "https://www.weather.com",
            "accuweather": "https://www.accuweather.com",
            "bbc weather": "https://www.bbc.com/weather",
            
            "wikihow": "https://www.wikihow.com",
            "howstuffworks": "https://www.howstuffworks.com",
            "lifehacker": "https://www.lifehacker.com",
            
            "zoom": "https://www.zoom.us",
            "slack": "https://www.slack.com",
            "microsoft teams": "https://www.microsoft.com/en-us/microsoft-teams/group-chat-software",
            "skype": "https://www.skype.com",
            
            "dropbox": "https://www.dropbox.com",
            "google drive": "https://drive.google.com",
            "one drive": "https://onedrive.live.com",
            "box": "https://www.box.com"
        }

    
    # Expression régulière pour capturer des variations de l'expression
    pattern = r"va\s+(sur\s+le\s+site\s+web\s+de\s+)?(.*)"  # Capture après "va sur le site web de"
    match = re.search(pattern, query)
    
    if match:
        # Extraire le nom du site après l'expression "va sur le site web de"
        site_name = match.group(2).strip()
        
        # Vérifier si le site correspond à l'un des sites connus
        if site_name in site_map:
            speak(f"Ouverture du site {site_name}")
            webbrowser.open(site_map[site_name])  # Ouvrir le site dans le navigateur par défaut
        else:
            speak(f"Je ne connais pas le site {site_name}. Voulez-vous essayer une recherche en ligne ?")
    else:
        speak("Je n'ai pas compris l'adresse du site. Pouvez-vous reformuler ?")

# Fin fontion pour ouverture des sites web

# Debut de fonction de gestion des reponses pré_enregistre

def load_responses():
    """Charge les réponses préenregistrées depuis le fichier JSON."""
    try:
        with open(os.path.join("engine", "responses.json"), "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("❌ Fichier de réponses non trouvé.")
        return {}
    except json.JSONDecodeError:
        print("❌ Erreur de lecture du fichier JSON.")
        return {}

responses = load_responses()

def get_best_match(query, responses):
    """Trouve la meilleure correspondance en utilisant fuzzy matching."""
    for category in responses:
        # Chercher la meilleure correspondance dans chaque catégorie de réponses
        best_match = process.extractOne(query, responses[category].keys(), scorer=fuzz.partial_ratio)

        if best_match and best_match[1] >= 80:  # seuil de similarité (80%)
            return responses[category][best_match[0]]

    return None  # Si aucune correspondance n'est trouvée

def handle_conversation(query):
    """Gère les conversations courantes en fonction des requêtes de l'utilisateur."""
    query = query.lower().strip()

    # Recherche d'une réponse préenregistrée avec fuzzywuzzy
    response = get_best_match(query, responses)

    if response:
        #speak(response)
        return response
    
    
# fin fonction de gestion de conversation

# Debut de fonction de detections des mots_clés


def hotword():
    """Détecte 'Nemos', 'Alexa' ou 'Siri' pour activer l'écoute automatique."""
    porcupine = None
    paud = None
    audio_stream = None

    try:
        # 🔹 Remplace par ta propre clé Picovoice
        access_key = "RECc3J5H3D+NxWZ6eBvfR0fiIsZsazly8Em2LyzQbkOdi8eoJLgQKQ=="

        # Initialisation de Porcupine avec les mots-clés et la clé d'accès
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["terminator", "picovoice", "americano", "hey siri", "jarvis"]
        )
        
        # Initialisation de PyAudio
        paud = pyaudio.PyAudio()
        
        # Ouverture du flux audio
        audio_stream = paud.open(rate=porcupine.sample_rate,
                                 channels=1,
                                 format=pyaudio.paInt16,
                                 input=True,
                                 frames_per_buffer=porcupine.frame_length)

        print("🎙️ Détection des hotwords activée...")

        # Boucle d'écoute pour la détection des hotwords
        while True:
            # Lecture de données audio à partir du flux
            keyword = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

            # Traitement du son pour détecter un mot-clé
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("✅ Hotword détecté ! Activation de l'écoute...")

                # Simuler une pression sur le raccourci (modifie si nécessaire)
                pyautogui.keyDown("win")  # Appuie sur la touche Win
                pyautogui.press("j")  # Presse la touche "j"
                time.sleep(0.5)
                pyautogui.keyUp("win")  # Relâche la touche Win

    except Exception as e:
        print(f"❌ Erreur dans hotword(): {e}")

    finally:
        # Nettoyage des ressources
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

# fin fonction de detection de mots clees

#Chat Bot

# Remplace par tes informations de connexion Hugging Face
HF_USERNAME = "codotoafodesamloik@gmail.com"
HF_PASSWORD = "Sam.97444805"
HUGGINGFACE_TOKEN = "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"

# Fonction pour se connecter à Hugging Face
def connect_huggingface():
    try:
        # Connexion avec identifiants (cookies)
        sign = Login(HF_USERNAME, HF_PASSWORD)
        cookies = sign.login()
        chatbot = hugchat.ChatBot(cookies=cookies)
        print("✅ Connexion réussie avec Hugging Face (cookies)")
        return chatbot, None  # Retourne le chatbot connecté
    except Exception as e:
        print(f"❌ Erreur de connexion avec les identifiants : {e}")
        print("🔄 Passage à l'InferenceClient avec token...")

        try:
            # Utilisation du token si la connexion avec identifiants échoue
            client = InferenceClient(model="mistralai/Mistral-Nemo-Instruct-2407", token=HUGGINGFACE_TOKEN)
            print("✅ Connexion réussie avec InferenceClient (token)")
            return None, client  # Retourne l'InferenceClient
        except Exception as e:
            print(f"❌ Échec de la connexion à Hugging Face avec le token : {e}")
            return None, None  # Échec total

# Initialiser la connexion Hugging Face
chatbot, client = connect_huggingface()

def chatBot(query):
    """Utilise response.json, la base de données et Hugging Face pour répondre."""
    
    # 1. Vérifier dans response.json
    response_json = handle_conversation(query)
    if response_json:
        print(f"🔹 Réponse trouvée (response.json) : {response_json}")
        speak(response_json)
        return response_json

    # 2. Vérifier dans la base de données
    response_db = get_from_db(query)
    if response_db:
        print(f"🔹 Réponse trouvée (base de données) : {response_db}")
        speak(response_db)
        return response_db

    # 3. Si la réponse n'est pas trouvée, utiliser Hugging Face
    try:
        if chatbot:
            print("🤖 Utilisation du chatbot Hugging Face...")
            raw_response = chatbot.chat(query)

            # Vérification si raw_response est un objet et contient du texte
            if hasattr(raw_response, 'text'):
                raw_response = raw_response.text  # Extraire seulement le texte

        elif client:
            print("🤖 Utilisation de l'InferenceClient...")
            raw_response = client.text_generation(query, max_new_tokens=200)

        else:
            raise ValueError("Aucune connexion valide à Hugging Face.")

        # Vérifier si la réponse est valide
        if not raw_response or not isinstance(raw_response, str) or len(raw_response.strip()) == 0:
            raise ValueError("Réponse vide ou invalide reçue de l'API Hugging Face.")

        # Séparer les phrases et en afficher 3 maximum
        sentences = raw_response.split('. ')
        short_response = '. '.join(sentences[:3]).strip()  
        if not short_response.endswith('.'):
            short_response += '.'

        print(f"🤖 Réponse générée : {short_response}")
        speak(short_response)  # Lecture de la réponse courte
        
        # Sauvegarde en base de données pour la prochaine fois
        save_to_db(query, short_response)

        return short_response

    except Exception as e:
        print(f"❌ Erreur lors de la génération de réponse : {e}")
        error_message = "Je ne peux pas répondre pour l'instant."
        speak(error_message)
        return error_message