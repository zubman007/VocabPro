"""Speech generation; editor-facing API is in app.services.api."""
from app.repositories.api_settings import audio_path, load_settings
from app.services.api_http import download_audio
from app.shared.messages import UserMessageError

VOICES = {
    "Spanish": "IKne3meq5aSn9XLyUdCD",
    "English": "hpp4J3VqNfWAUOO0d1Us",
    "German": "onwK4e9ZLuTAKqWW03F9",
    "French": "FGY2WhTYpPnrIDTdsKH5",
}


def generate_audio(i,frame,language,learning_by,*,settings_path=None):
    if language not in VOICES:
        raise UserMessageError('No speech voice configured for {language}', language=language)
    token = load_settings(settings_path).get("11Labs token", "")
    if not token:
        raise ValueError("Missing ElevenLabs token")
    download_audio(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES[language]}/stream",
        audio_path(learning_by,language,frame.loc[i,"ID"],settings_path),
        method="POST", headers={"Accept": "application/json", "xi-api-key": token},
        json={"text": frame.loc[i, language], "model_id": "eleven_v3",
              "voice_settings": {"stability": 0.5, "similarity_boost": 0.8,
                                 "style": 0.0, "use_speaker_boost": True}},
    )
    frame.at[i, "Audio"] = "Automatic - 11Labs"
    return frame
