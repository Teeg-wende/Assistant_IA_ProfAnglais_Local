# 🎙️ Assistant vocal bilingue (Français / Anglais) avec Mistral et reconnaissance vocale

Ce projet permet d'interagir vocalement avec un assistant IA, en français ou en anglais, grâce à la reconnaissance vocale et au modèle **Mistral 7B**.  
Il peut agir soit comme **professeur d'anglais**, soit comme **ami francophone**, avec réponses parlées grâce à la synthèse vocale.

---

## ✨ Fonctionnalités

- **Enregistrement audio** depuis le microphone
- **Transcription vocale** avec Google Speech Recognition
- **Analyse et génération de réponse** via le modèle **Mistral 7B (llama.cpp)**
- **Synthèse vocale** avec Google Text-to-Speech (gTTS)
- Deux modes d’interaction :
  1. **Professeur d’anglais** : analyse et corrige les phrases, explique les erreurs et pose des questions
  2. **Ami francophone** : conversation naturelle et chaleureuse

---

## 📦 Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/Teeg-wende/Assistant_IA_ProfAnglais_Local.git
cd Assistant_IA_ProfAnglais_Local
```

### 2. Créer un environnement virtuel (optionnel mais recommandé)
```bash
python3 -m venv venv
source venv/bin/activate   # sous Linux / Mac
venv\Scripts\activate      # sous Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

**Exemple de `requirements.txt` :**
```
pyaudio
SpeechRecognition
gTTS
llama-cpp-python
```

⚠️ Sur Linux, il faut installer les dépendances système pour PyAudio :
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

---

## 📂 Préparer le modèle Mistral

1. Télécharger le modèle **mistral-7b-instruct-v0.2.Q4_K_M.gguf** depuis Hugging Face ou TheBloke :
   - [Lien HuggingFace - Mistral 7B](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)
2. Placer le fichier `.gguf` dans un dossier `models/` à la racine du projet.

Arborescence :
```
.
├── models/
│   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf
├── assistant.py
├── requirements.txt
└── README.md
```

---

## 🚀 Utilisation

Lance le script principal :
```bash
python assistant.py
```

Fonctionnement :
1. L’assistant détecte ton micro
2. Il enregistre ta voix pendant quelques secondes
3. Il transcrit le texte
4. Il envoie le texte au modèle **Mistral**
5. Il répond à voix haute

---

## 🎯 Exemple d’utilisation

**Mode Ami** :
> Toi : Salut, comment tu vas aujourd’hui ?  
> Assistant : Ça va très bien merci, et toi comment s’est passée ta journée ?

**Mode Professeur** :
> Toi (en anglais) : I goes to the park yesterday.  
> Assistant : I went to the park yesterday. You should use the past tense "went" instead of "goes" when speaking about the past. This is a statement so I’m glad you enjoyed your walk. What did you see there?

---

## 🛠️ Personnalisation

- Pour passer en **mode professeur** :  
  Modifie la ligne :
  ```python
  reponse = obtenir_reponse(texte, prompt=prompt_professeur)
  ```
- Pour rester en **mode ami** :  
  Garde :
  ```python
  reponse = obtenir_reponse(texte, prompt=prompt_ami)
  ```

---

## 📜 Licence

Ce projet est sous licence MIT.  
Tu peux l’utiliser, le modifier et le redistribuer librement.

---

## ❤️ Remerciements

- [Mistral AI](https://mistral.ai/) pour le modèle
- [llama.cpp](https://github.com/ggerganov/llama.cpp) pour l’inférence CPU/GPU
- [Google Speech Recognition](https://pypi.org/project/SpeechRecognition/) pour la transcription
- [gTTS](https://pypi.org/project/gTTS/) pour la synthèse vocale
