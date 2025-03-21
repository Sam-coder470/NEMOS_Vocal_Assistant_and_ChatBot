import pyttsx3
import speech_recognition as sr
import eel
import time
import re

import pyttsx3
import eel
import re

def speak(text):
    """Convertit du texte en parole avec une voix masculine naturelle et un rendu fluide."""
    text = str(text).encode('utf-8').decode('utf-8')  # S'assurer que le texte est en UTF-8

    # Initialisation de pyttsx3
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')

    # Sélectionner une voix masculine disponible
    male_voice_found = False
    for voice in voices:
        if "male" in voice.name.lower() or "hugo" in voice.name.lower() or "paul" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            male_voice_found = True
            break

    # Si aucune voix masculine n'est trouvée, on utilise la première voix par défaut
    if not male_voice_found and voices:
        engine.setProperty('voice', voices[0].id)

    # Réglage de la vitesse et du volume pour un rendu plus naturel
    engine.setProperty('rate', 170)  # Réduction de la vitesse pour éviter un débit trop rapide
    engine.setProperty('volume', 1.0)  # Volume au maximum

    # Afficher le texte dans l'interface
    eel.DisplayMessage(text)

    # Gestion intelligente de la ponctuation (ajout de pauses naturelles)
    text = re.sub(r"([.!?])", r"\1 |", text)  # Ajout d'une légère pause après les points, exclamations et interrogations

    # Lancer la synthèse vocale
    engine.say(text)
    eel.receiverText(text)  # Envoyer le texte affiché dans l'interface
    engine.runAndWait()


def takecommand():
    """Écoute l'utilisateur, reconnaît la parole et retourne le texte."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 En écoute...")
        eel.DisplayMessage(" En écoute...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source,duration=1)  # Correction ici
        
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=6)  # Correction ici
            print('🔍 Reconnaissance en cours...')
            eel.DisplayMessage(' Reconnaissance en cours...')
            query = r.recognize_google(audio, language='fr-FR')
            print(f"🗣️ Utilisateur a dit : {query}\n")
            eel.DisplayMessage(query)
            #speak(query)  # Faire parler l'assistant avec la phrase reconnue
            time.sleep(2)
            return query.lower()
        except sr.UnknownValueError:
            print("❌ Impossible de comprendre l'audio.")
            eel.DisplayMessage(" Impossible de comprendre l'audio.")
            eel.ShowHood()
            return ""
        except sr.RequestError:
            print("⚠️ Erreur avec le service de reconnaissance vocale.")
            eel.DisplayMessage("Erreur avec le service de reconnaissance vocale.")
            eel.ShowHood()
            return ""
        except Exception as e:
            print(f"⚠️ Erreur inattendue : {str(e)}")
            eel.DisplayMessage(" Erreur inattendue :", {str(e)})
            eel.ShowHood()
            return ""

@eel.expose
def allCommands(message=1):
    """Gère les commandes vocales et textuelles avec Hugging Face comme chatbot principal."""

    import re
    import eel  # Import local pour éviter les conflits
    from engine.features import chatBot  # Import unique du chatbot Hugging Face

    if message == 1:
        query = takecommand()
        if not query:
            print("❌ Aucune commande détectée.")
            return
        query = query.lower().strip()
        print(f"🔹 Commande reçue (voix) : {query}")

    else:
        query = message.lower().strip()
        print(f"🔹 Commande reçue (texte) : {query}")

    eel.senderText(query)  # Affichage dans l'interface

    try:
        if re.search(r"^(ouvre|lance)\s+([\w\s]+)", query):
            print("📂 Ouverture d'application détectée...")
            from engine.features import openCommand  # Import local
            openCommand(query)

        elif re.search(r"^(joue|mets|play)\s+([\w\s]+)\s+(sur|dans)\s+youtube", query):
            print("▶️ Lecture YouTube détectée...")
            from engine.features import PlayYoutube  # Import local
            PlayYoutube(query)

        elif re.search(r"^(va|ouvre)\s+(sur\s+le\s+site\s+web\s+de\s+)?([\w\s]+)", query):
            print("🌍 Ouverture de site web détectée...")
            from engine.features import openWebsite  # Import local
            openWebsite(query)

        else:
            print("🤖 Utilisation du chatbot Hugging Face...")
            from engine.features import chatBot 
            chatBot(query)

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de la commande : {e}")

    eel.ShowHood()