from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os
import shutil
import tempfile
import json
import time
import requests

print("💡 CURRENT FILE:", __file__)


print("Running main.py at", time.strftime("%Y-%m-%d %H:%M:%S"))
print("File path:", __file__)

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_API_ORG")
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")




@app.get("/")
def read_root():
    html_file = Path("static/index.html")
    print("📄 Looking for:", html_file.absolute())

    try:
        content = html_file.read_text(encoding="utf-8")
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        print("❌ Error loading index.html:", e)
        return HTMLResponse(content=f"<h1>Error loading index.html: {e}</h1>", status_code=500)


@app.get("/play")
def play_audio():
    audio_file = Path("output.mp3")
    if audio_file.exists():
        return FileResponse(audio_file, media_type="audio/mpeg", filename="output.mp3")
    return {"error": "No audio file found. Please run /talk first."}

@app.post("/talk")
async def post_audio(file: UploadFile = File(...), stream_audio: bool = Query(False)):
    print("📥 /talk endpoint hit. Filename:", file.filename)
    try:
        start = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        print("⏱️ File saved at", tmp_path)

        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        os.remove(tmp_path)
        print("🧠 Whisper raw response:", transcript)

        user_message = transcript.text.strip()
        print("📝 Transcribed Text:", repr(user_message))

        if not user_message:
            return {"error": "Empty transcription. Please check your audio clarity."}

        from random import randint
        context_id = f"context_{randint(1000, 9999)}"
        user_message_with_context = f"{user_message} [{context_id}]"

        messages = [
            {"role": "system", "content": "You are Arth, a witty general knowledge teacher. Always generate unique, funny, short replies."},
            {"role": "user", "content": user_message_with_context}
        ]

        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        ).choices[0].message.content

        print("✅ GPT response ready")

        eleven_key = os.getenv("ELEVENLABS_KEY")
        voice_id = "UgBBYS2sOqTuMpoF3BR0"
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": eleven_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": gpt_response,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.7
            }
        }

        audio_path = "output.mp3"
        try:
            print("🔊 Sending TTS request...")
            response = requests.post(tts_url, headers=headers, json=payload, timeout=10)
            print("📡 TTS Status Code:", response.status_code)
            if response.status_code == 200:
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                print("✅ TTS audio saved")
            else:
                try:
                    error_json = response.json()
                    error_detail = error_json.get("message") or response.text
                except Exception:
                    error_detail = response.text
                print(f"❌ ElevenLabs error {response.status_code}:", error_detail)
                audio_path = f"TTS failed {response.status_code}: {error_detail}"
        except Exception as e:
            print("❌ TTS Exception:", e)
            audio_path = f"TTS error: {str(e)}"

        if stream_audio and Path(audio_path).exists():
            return FileResponse(audio_path, media_type="audio/mpeg", filename="response.mp3")

        return {
            "transcript": user_message,
            "context_id": context_id,
            "response": gpt_response,
            "audio_file": audio_path
        }

    except Exception as e:
        import traceback
        print("❌ Error in /talk:", e)
        traceback.print_exc()
        return {"error": str(e)}
