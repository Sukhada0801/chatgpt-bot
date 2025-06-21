from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os
import shutil
import tempfile
import json
import time

print("Running main.py at", time.strftime("%Y-%m-%d %H:%M:%S"))
print("File path:", __file__)

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_API_ORG")
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/talk")
async def post_audio(file: UploadFile = File(...)):
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

        print("✅ Whisper transcript received")
        user_message = transcript.text

        return {
            "transcript": user_message,
            "response": "Skipping GPT and TTS to isolate whisper",
            "audio_file": "TTS skipped"
        }

    except Exception as e:
        import traceback
        print("❌ Error in /talk:", e)
        traceback.print_exc()
        return {"error": str(e)}
