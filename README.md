

This project enables users to ask questions by speaking, and receive an audio response. It uses OpenAI’s Whisper API for speech-to-text transcription, GPT-4o for generating a response, and ElevenLabs to convert the response back to speech.

Includes a browser-based interface to record your voice and hear the answer—no typing needed.

---

## How It Works

1. Record Your Voice using the browser (Start/Stop).
2. Whisper API** transcribes the voice into text.
3. GPT-4o processes the query and generates a relevant text response.
4. ElevenLabs API converts that text to speech.
5. Audio Response is played back in the browser + text is shown.

---

## 🛠️ Tech Stack

| Component           | Technology          |
|--------------------|---------------------|
| Frontend UI        | HTML + JavaScript   |
| Backend API        | FastAPI (Python)    |
| Transcription      | OpenAI Whisper API  |
| Text Generation    | OpenAI GPT-4o       |
| Text-to-Speech     | ElevenLabs API      |

---
Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/voice-qa-bot.git
cd voice-qa-bot
```

### 2. Add `.env` File

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your_openai_key
OPENAI_API_ORG=your_openai_org
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet:

```bash
pip install fastapi uvicorn python-dotenv openai requests
```

### 4. Run Backend

```bash
uvicorn main:app --reload
```

### 5. Run Frontend

Open `index.html` in a browser (recommended: Live Server extension in VSCode or a local server).

---

## 🔐 API Requirements

- **OpenAI API key**: for Whisper + GPT-4o
- **ElevenLabs API key**: for high-quality speech synthesis

---

## 🌱 Use Cases

- General knowledge Q&A
- Domain-specific queries (e.g., finance, health, tech)
- Accessibility tools
- Educational voice bots

---
