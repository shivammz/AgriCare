import requests

url = "https://indic-parler-tts-ws-4b-8080-ab249c.ml.iit-ropar.truefoundry.cloud"
payload = {
    "text": "नमस्ते, यह एक परीक्षण है।",
    "language": "hi",
    "speaker": "hindi"
}

resp = requests.post(url, json=payload)
resp.raise_for_status()

# Save wav
with open("output.wav", "wb") as f:
    f.write(resp.content)
print("WAV saved to output.wav")
