import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from app.multimodal.schemas import NormalizedInput, AudioTranscript
from app.multimodal.providers.speech import get_speech_provider, SpeechProvider

class AudioProcessor:
    """
    Processes audio recordings (.wav, .mp3, .m4a) through Speech-to-Text provider abstraction.
    Transforms spoken dialogue into normalized textual content suitable for RAG or QLoRA fine-tuning.
    """
    @staticmethod
    async def process_file(file_path: Path, provider: Optional[SpeechProvider] = None) -> NormalizedInput:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        speech_provider = provider or get_speech_provider()
        transcript: AudioTranscript = await speech_provider.transcribe(file_path)

        if not transcript.text or not transcript.text.strip():
            raise ValueError(f"Transcription resulted in empty content for {file_path.name}")

        return NormalizedInput(
            id=f"norm-aud-{uuid.uuid4().hex[:8]}",
            modality="audio",
            content=transcript.text.strip(),
            source=file_path.name,
            metadata={
                "filename": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "provider": transcript.provider,
                "duration_seconds": transcript.duration_seconds,
                "language": transcript.language,
                "has_segments": transcript.segments is not None and len(transcript.segments) > 0
            }
        )
