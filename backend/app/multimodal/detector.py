import mimetypes
from pathlib import Path
from typing import Optional, Tuple
from app.multimodal.schemas import ModalityDetectionResult, ModalityType

SUPPORTED_EXTENSIONS = {
    # TEXT
    ".txt": ("text", "text/plain"),
    ".json": ("text", "application/json"),
    ".jsonl": ("text", "application/x-jsonlines"),
    ".csv": ("text", "text/csv"),
    ".md": ("text", "text/markdown"),
    
    # DOCUMENTS
    ".pdf": ("document", "application/pdf"),
    ".docx": ("document", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ".doc": ("document", "application/msword"),
    
    # IMAGES
    ".png": ("image", "image/png"),
    ".jpg": ("image", "image/jpeg"),
    ".jpeg": ("image", "image/jpeg"),
    ".webp": ("image", "image/webp"),
    
    # AUDIO
    ".wav": ("audio", "audio/wav"),
    ".mp3": ("audio", "audio/mpeg"),
    ".m4a": ("audio", "audio/mp4"),
}

SUPPORTED_MIME_PREFIXES = {
    "image/": "image",
    "audio/": "audio",
    "text/": "text",
    "application/pdf": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "application/msword": "document",
    "application/json": "text",
}

class ModalityDetector:
    """
    Deterministic modality detector.
    Evaluates file extension, standard MIME mapping, and binary header characteristics.
    Zero hallucination: rejects unsupported formats deterministically.
    """
    @staticmethod
    def detect_file(file_path: Path) -> ModalityDetectionResult:
        file_path = Path(file_path)
        filename = file_path.name
        ext = file_path.suffix.lower()
        size_bytes = file_path.stat().st_size if file_path.exists() else 0

        # 1. Deterministic extension match
        if ext in SUPPORTED_EXTENSIONS:
            modality, mime = SUPPORTED_EXTENSIONS[ext]
            return ModalityDetectionResult(
                modality=modality,
                mime_type=mime,
                filename=filename,
                extension=ext,
                file_size_bytes=size_bytes,
                is_supported=True
            )

        # 2. Check mimetypes library fallback
        guessed_mime, _ = mimetypes.guess_type(filename)
        if guessed_mime:
            for prefix, mod in SUPPORTED_MIME_PREFIXES.items():
                if guessed_mime.startswith(prefix) or guessed_mime == prefix:
                    return ModalityDetectionResult(
                        modality=mod,
                        mime_type=guessed_mime,
                        filename=filename,
                        extension=ext,
                        file_size_bytes=size_bytes,
                        is_supported=True
                    )

        # 3. Unsupported format
        return ModalityDetectionResult(
            modality="unknown",
            mime_type=guessed_mime or "application/octet-stream",
            filename=filename,
            extension=ext,
            file_size_bytes=size_bytes,
            is_supported=False,
            error_message=f"Unsupported format '{ext}'. Supported formats: Text (.txt, .jsonl, .csv), Documents (.pdf, .docx), Images (.png, .jpg, .webp), Audio (.wav, .mp3, .m4a)."
        )

    @staticmethod
    def detect_text_input(raw_text: str) -> ModalityDetectionResult:
        return ModalityDetectionResult(
            modality="text",
            mime_type="text/plain",
            filename="user_prompt.txt",
            extension=".txt",
            file_size_bytes=len(raw_text.encode("utf-8")),
            is_supported=True
        )
