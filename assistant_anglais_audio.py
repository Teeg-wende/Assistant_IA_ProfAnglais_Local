import pyaudio
import wave
import speech_recognition as sr
from gtts import gTTS
import os
import re
from llama_cpp import Llama

# -------------------------------------------------------------------
# Prompts utilisés pour le professeur et l'ami
# -------------------------------------------------------------------

prompt_professeur = (
    "You are a certified bilingual English-French teacher. "
    "Carefully analyze the student's input for grammar vocabulary spelling or pronunciation errors "
    "ignoring all punctuation marks as the input comes from audio transcription. "
    "Focus on the meaning and the rules of English grammar rather than the punctuation. "
    "Respond in a single compact paragraph without line breaks numbers or special characters. "
    "Start by giving the corrected sentence in natural English if there are any errors otherwise "
    "repeat the student's sentence as is. Then clearly explain the corrections in plain simple language "
    "highlighting why they are necessary. Next determine if the student's input is a question or a statement. "
    "If it is a question, provide a clear and direct answer. If it is a statement, respond appropriately to "
    "acknowledge or continue the conversation. Always end your response with a short related follow-up question "
    "to keep the conversation going. Use clear natural English unless the student explicitly requests a response "
    "in French. If pronunciation help is relevant include in French Tu devrais prononcer correctement cette phrase "
    "comme ceci followed by the correct pronunciation. If the student's input is unclear politely ask them to "
    "rephrase their message. Keep your tone professional friendly and encouraging. Your response should be concise "
    "clear and easy to understand fitting within 250 tokens. Never skip the correction step when there are errors "
    "but do not force corrections if the sentence is already correct. Always respond entirely in one language per "
    "message either English or French except when briefly explaining a word or phrase from one language into the other. "
    "Here is the question "
)

prompt_ami = (
    "Tu es un ami de compagnie. "
    "Tu parles exclusivement en français, de façon claire, naturelle et chaleureuse. "
    "Tu n'hésites pas à poser des questions pour mieux comprendre et approfondir tes échanges. "
    "Tes réponses sont orientées vers le soutien, la complicité et une vision tournée vers l’avenir. "
    "Tes réponses sont toujours concises et claires, sans lignes vides ni caractères spéciaux. "
    "Si tu reçois une question, tu réponds clairement. Si c'est une affirmation, tu la reconnais ou fais évoluer par une réponse adaptée. "
    "Tu termines toujours ta réponse par une question courte et liée au sujet pour continuer la conversation. "
    "Voici la question de ton ami :"
)

# -------------------------------------------------------------------
# Fonction de nettoyage du texte retourné par le modèle
# -------------------------------------------------------------------

def nettoyer_texte(texte):
    """Supprime numéros, deux-points, retours à la ligne et espaces superflus."""
    texte = re.sub(r'\d+\.', '', texte)
    texte = re.sub(r':', '', texte)
    texte = re.sub(r'\n', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte)
    return texte.strip()

# -------------------------------------------------------------------
# Initialisation du modèle Llama
# -------------------------------------------------------------------

chemin_modele = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
nombre_threads = 11
max_context = 32768
gpu_layers = 6

modele_llm = Llama(
    model_path=chemin_modele,
    n_ctx=max_context,
    n_threads=nombre_threads,
    n_gpu_layers=gpu_layers,
    verbose=False
)

# -------------------------------------------------------------------
# Fonction pour générer la réponse du modèle
# -------------------------------------------------------------------

def obtenir_reponse(entree_utilisateur, prompt=prompt_ami):
    """Génère une réponse texte via le modèle à partir de l'entrée utilisateur et d'un prompt donné."""
    requete = prompt + entree_utilisateur
    reponse = modele_llm(requete, max_tokens=120, temperature=0.7)
    texte_nettoye = nettoyer_texte(reponse['choices'][0]['text'])
    return texte_nettoye

# -------------------------------------------------------------------
# Détection et sélection du périphérique audio d'entrée
# -------------------------------------------------------------------

def detecter_peripherique_audio(auto_selection=True):
    """Liste les périphériques d'entrée audio et sélectionne automatiquement le premier trouvé."""
    p = pyaudio.PyAudio()
    meilleur_index = None
    meilleur_nom = None

    print("Liste des périphériques audio disponibles :\n")

    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        nom = dev['name']
        canaux_entree = dev['maxInputChannels']
        api_hote = p.get_host_api_info_by_index(dev['hostApi'])['name']

        if canaux_entree > 0:
            print(f"{i}: {nom} (API: {api_hote}, Canaux: {canaux_entree})")
            if meilleur_index is None and auto_selection:
                meilleur_index = i
                meilleur_nom = nom

    p.terminate()

    if meilleur_index is not None:
        print(f"Périphérique auto-sélectionné : {meilleur_index} - {meilleur_nom}")
        return meilleur_index
    else:
        print("Aucun périphérique d'entrée détecté.")
        return None

# -------------------------------------------------------------------
# Recherche d'un taux d'échantillonnage compatible
# -------------------------------------------------------------------

def trouver_taux_echantillonnage(index_peripherique):
    """Teste différents taux d’échantillonnage courants et retourne le premier compatible."""
    p = pyaudio.PyAudio()
    for taux in [44100, 22050, 16000, 8000]:
        try:
            flux = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=taux,
                          input=True,
                          input_device_index=index_peripherique)
            flux.close()
            p.terminate()
            print(f"Taux d’échantillonnage compatible trouvé : {taux} Hz")
            return taux
        except Exception:
            continue
    p.terminate()
    print("Aucun taux d’échantillonnage compatible trouvé.")
    return None

# -------------------------------------------------------------------
# Enregistrement audio
# -------------------------------------------------------------------

def enregistrer_audio(index_peripherique, duree=40, nom_fichier="enregistrement.wav", taux_echantillonnage=16000):
    """Enregistre l'audio du périphérique donné pendant une durée spécifiée et sauvegarde en WAV."""
    if index_peripherique is None:
        print("Aucun périphérique valide sélectionné, enregistrement annulé.")
        return False

    p = pyaudio.PyAudio()
    try:
        flux = p.open(format=pyaudio.paInt16,
                      channels=1,
                      rate=taux_echantillonnage,
                      input=True,
                      input_device_index=index_peripherique)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du flux audio : {e}")
        p.terminate()
        return False

    print(f"Enregistrement en cours (device {index_peripherique}, {taux_echantillonnage} Hz) pendant {duree}s...")
    frames = []

    for _ in range(0, int(taux_echantillonnage / 1024 * duree)):
        try:
            data = flux.read(1024)
        except Exception as e:
            print(f"Erreur lors de la lecture audio : {e}")
            break
        frames.append(data)

    flux.stop_stream()
    flux.close()
    p.terminate()

    try:
        with wave.open(nom_fichier, 'wb') as fichier_wave:
            fichier_wave.setnchannels(1)
            fichier_wave.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            fichier_wave.setframerate(taux_echantillonnage)
            fichier_wave.writeframes(b''.join(frames))
        print(f"Enregistrement sauvegardé dans {nom_fichier}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier WAV : {e}")
        return False

# -------------------------------------------------------------------
# Transcription audio en texte
# -------------------------------------------------------------------

def transcrire_audio(nom_fichier, langue="fr-FR"):
    """Transcrit un fichier audio en texte avec la reconnaissance vocale Google."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(nom_fichier) as source:
            audio_data = recognizer.record(source)
        texte_transcrit = recognizer.recognize_google(audio_data, language=langue)
        print("\nTranscription :")
        print(texte_transcrit)
        return texte_transcrit
    except sr.UnknownValueError:
        print("La reconnaissance vocale n'a pas pu comprendre l'audio.")
    except sr.RequestError as e:
        print(f"Erreur du service Google Speech : {e}")
    return None

# -------------------------------------------------------------------
# Synthèse vocale du texte
# -------------------------------------------------------------------

def synthese_vocale(texte, langue='fr', nom_fichier='tts_output.mp3'):
    """Convertit un texte en audio puis le joue (Linux)."""
    if not texte:
        print("Pas de texte à vocaliser.")
        return

    tts = gTTS(text=texte, lang=langue, slow=False)
    tts.save(nom_fichier)
    print(f"Synthèse vocale sauvegardée dans {nom_fichier}")

    os.system(f"mpg123 {nom_fichier}")

# -------------------------------------------------------------------
# Configuration périphérique audio
# -------------------------------------------------------------------

def configurer_peripherique_audio():
    """Détecte et configure le périphérique audio et son taux d’échantillonnage."""
    device = detecter_peripherique_audio()
    if device is None:
        print("Aucun périphérique d'entrée détecté, impossible d'enregistrer.")
        return None, None
    taux = trouver_taux_echantillonnage(device)
    if taux is None:
        print("Aucun taux d'échantillonnage compatible, impossible d'enregistrer.")
        return None, None
    return device, taux

# -------------------------------------------------------------------
# Enregistrement et transcription combinés
# -------------------------------------------------------------------

def enregistrer_et_transcrire(device, taux, nom_fichier="whatsapp_audio.wav", duree=17):
    """Enregistre l’audio, puis le transcrit en texte."""
    print("Enregistrement en cours...")
    succes = enregistrer_audio(device, duree=duree, nom_fichier=nom_fichier, taux_echantillonnage=taux)
    if not succes:
        print("Enregistrement échoué, transcription annulée.")
        return None
    print("Transcription en cours...")
    texte = transcrire_audio(nom_fichier)
    if not texte:
        print("Transcription vide, synthèse vocale annulée.")
        return None
    return texte

# -------------------------------------------------------------------
# Traitement texte et synthèse vocale
# -------------------------------------------------------------------

def traiter_et_parler(texte):
    """Envoie le texte au modèle, récupère la réponse et la vocalise."""
    print("Assistant")
    reponse = obtenir_reponse(texte)
    print("Synthèse vocale en cours...")
    synthese_vocale(reponse, lang='fr')
    print("Réponse :", reponse)
    return reponse

# -------------------------------------------------------------------
# Boucle principale de conversation
# -------------------------------------------------------------------

def demarrer_conversation():
    """Configure l'audio puis lance la boucle d’enregistrement, transcription et réponse."""
    device, taux = configurer_peripherique_audio()
    if device is None or taux is None:
        return
    while True:
        texte = enregistrer_et_transcrire(device, taux)
        if texte is not None:
            traiter_et_parler(texte)

# -------------------------------------------------------------------
# Point d’entrée du script
# -------------------------------------------------------------------

if __name__ == '__main__':
    demarrer_conversation()
