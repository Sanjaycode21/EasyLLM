import os
import base64
import mimetypes
import httpx
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from app.config import settings
from app.multimodal.schemas import VisionAnalysis

class VisionProviderError(Exception):
    pass

class VisionProvider(ABC):
    @abstractmethod
    async def analyze_image(self, image_path: Path) -> VisionAnalysis:
        """
        Analyzes the image to extract visual content, semantic description, and any printed/OCR text.
        """
        pass

class GeminiVisionProvider(VisionProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    async def analyze_image(self, image_path: Path) -> VisionAnalysis:
        if not image_path.exists():
            raise VisionProviderError(f"Image file not found: {image_path}")

        mime_type, _ = mimetypes.guess_type(str(image_path))
        mime_type = mime_type or "image/png"

        with open(image_path, "rb") as f:
            image_bytes = f.read()
        b64_data = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "Analyze this image carefully for an enterprise AI knowledge pipeline. "
            "1. If there is any printed or handwritten text, tables, labels, diagrams, or OCR content, transcribe it thoroughly. "
            "2. Provide a clear, factual semantic description of what is depicted in the image."
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
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(self.base_url, json=payload)
                if res.status_code != 200:
                    raise VisionProviderError(f"Gemini Vision API error (HTTP {res.status_code}): {res.text}")
                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise VisionProviderError("Gemini Vision API returned no response candidates.")
                text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                return VisionAnalysis(
                    extracted_text=text_content,
                    description=text_content,
                    has_text=len(text_content.strip()) > 0,
                    provider=f"Gemini Vision ({self.model})",
                    structured_data={"file_size_bytes": len(image_bytes), "mime_type": mime_type}
                )
            except Exception as e:
                if isinstance(e, VisionProviderError):
                    raise e
                raise VisionProviderError(f"Failed to communicate with Gemini Vision API: {str(e)}")

class OpenAIVisionProvider(VisionProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def analyze_image(self, image_path: Path) -> VisionAnalysis:
        if not image_path.exists():
            raise VisionProviderError(f"Image file not found: {image_path}")

        mime_type, _ = mimetypes.guess_type(str(image_path))
        mime_type = mime_type or "image/png"

        with open(image_path, "rb") as f:
            image_bytes = f.read()
        b64_data = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "Analyze this image for an AI knowledge base. "
            "Extract all visible text/diagrams and describe the visual information accurately."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}}
                    ]
                }
            ],
            "max_tokens": 800
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(self.base_url, headers=headers, json=payload)
                if res.status_code != 200:
                    raise VisionProviderError(f"OpenAI Vision API error (HTTP {res.status_code}): {res.text}")
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                return VisionAnalysis(
                    extracted_text=content,
                    description=content,
                    has_text=len(content.strip()) > 0,
                    provider=f"OpenAI Vision ({self.model})",
                    structured_data={"file_size_bytes": len(image_bytes), "mime_type": mime_type}
                )
            except Exception as e:
                if isinstance(e, VisionProviderError):
                    raise e
                raise VisionProviderError(f"Failed to communicate with OpenAI Vision API: {str(e)}")

def get_vision_provider() -> VisionProvider:
    """
    Returns the active VisionProvider based on configured environment variables.
    Raises clear VisionProviderError if no provider is configured (Zero fake outputs).
    """
    if settings.gemini_api_key:
        return GeminiVisionProvider(settings.gemini_api_key, settings.gemini_model)
    elif settings.openai_api_key:
        return OpenAIVisionProvider(settings.openai_api_key, settings.openai_model)
    else:
        raise VisionProviderError(
            "No Vision Provider configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in your environment (.env) to enable image analysis and OCR."
        )
