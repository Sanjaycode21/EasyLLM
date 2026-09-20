import os
import base64
import mimetypes
import httpx
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from app.config import settings
from app.multimodal.schemas import AudioTranscript

class SpeechProviderError(Exception):
    pass

class SpeechProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: Path) -> AudioTranscript:
        """
        Transcribes the speech in the audio file to text.
        """
        pass

class GeminiSpeechProvider(SpeechProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    async def transcribe(self, audio_path: Path) -> AudioTranscript:
        if not audio_path.exists():
            raise SpeechProviderError(f"Audio file not found: {audio_path}")

        mime_type, _ = mimetypes.guess_type(str(audio_path))
        if not mime_type:
            ext = audio_path.suffix.lower()
            if ext == ".mp3":
                mime_type = "audio/mp3"
            elif ext == ".wav":
                mime_type = "audio/wav"
            elif ext == ".m4a":
                mime_type = "audio/m4a"
            else:
                mime_type = "audio/mpeg"

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        b64_data = base64.b64encode(audio_bytes).decode("utf-8")

        prompt = (
            "Transcribe the following audio recording accurately into text. "
            "Preserve speaker dialogue, key terminology, and conversational flow without summarization. "
            "Output only the faithful transcript."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": b64_data
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                res = await client.post(self.base_url, json=payload)
                if res.status_code != 200:
                    raise SpeechProviderError(f"Gemini Speech API error (HTTP {res.status_code}): {res.text}")
                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise SpeechProviderError("Gemini Speech API returned no transcription candidates.")
                transcript_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

                return AudioTranscript(
                    text=transcript_text,
                    provider=f"Gemini Audio ({self.model})"
                )
            except Exception as e:
                if isinstance(e, SpeechProviderError):
                    raise e
                raise SpeechProviderError(f"Failed to communicate with Gemini Speech API: {str(e)}")

class OpenAISpeechProvider(SpeechProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/audio/transcriptions"

    async def transcribe(self, audio_path: Path) -> AudioTranscript:
        if not audio_path.exists():
            raise SpeechProviderError(f"Audio file not found: {audio_path}")

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                with open(audio_path, "rb") as audio_file:
                    files = {
                        "file": (audio_path.name, audio_file, "audio/mpeg"),
                        "model": (None, "whisper-1"),
                        "response_format": (None, "verbose_json")
                    }
                    res = await client.post(self.base_url, headers=headers, files=files)
                    if res.status_code != 200:
                        raise SpeechProviderError(f"OpenAI Whisper API error (HTTP {res.status_code}): {res.text}")
                    data = res.json()
                    return AudioTranscript(
                        text=data.get("text", "").strip(),
                        language=data.get("language"),
                        duration_seconds=data.get("duration"),
                        provider="OpenAI Whisper (whisper-1)",
                        segments=data.get("segments")
                    )
            except Exception as e:
                if isinstance(e, SpeechProviderError):
                    raise e
                raise SpeechProviderError(f"Failed to communicate with OpenAI Whisper API: {str(e)}")

def get_speech_provider() -> SpeechProvider:
    """
    Returns the active SpeechProvider based on configured environment variables.
    Raises clear SpeechProviderError if no provider is configured (Zero fake transcripts).
    """
    if settings.gemini_api_key:
        return GeminiSpeechProvider(settings.gemini_api_key, settings.gemini_model)
    elif settings.openai_api_key:
        return OpenAISpeechProvider(settings.openai_api_key)
    else:
        raise SpeechProviderError(
            "No Speech-to-Text Provider configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in your environment (.env) to enable audio transcription."
        )
