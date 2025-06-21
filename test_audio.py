import requests

with open("voice.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8000/talk",
        files={"file": ("voice.mp3", f, "audio/mpeg")}
    )

print("Status Code:", response.status_code)
print("Response:", response.json())
