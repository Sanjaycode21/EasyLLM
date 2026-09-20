import re
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from app.multimodal.schemas import NormalizedInput

class TextProcessor:
    """
    Normalizes raw text files (.txt, .json, .jsonl, .csv, .md) and plain string inputs.
    Cleans encoding artifacts and non-printable characters while preserving semantic content.
    """
    @staticmethod
    def clean_text(raw_text: str) -> str:
        # Normalize line endings
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove null bytes and non-printable control characters except standard tabs and newlines
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        return text.strip()

    @staticmethod
    def process_file(file_path: Path) -> NormalizedInput:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        # Try utf-8 first, then fallback to latin-1/errors replace
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

        cleaned = TextProcessor.clean_text(content)
        lines = cleaned.split("\n")
        word_count = len(cleaned.split())

        return NormalizedInput(
            id=f"norm-txt-{uuid.uuid4().hex[:8]}",
            modality="text",
            content=cleaned,
            source=file_path.name,
            metadata={
                "filename": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "num_lines": len(lines),
                "word_count": word_count,
                "encoding": "utf-8"
            }
        )

    @staticmethod
    def process_string(text: str, source_label: str = "user_input") -> NormalizedInput:
        cleaned = TextProcessor.clean_text(text)
        return NormalizedInput(
            id=f"norm-txt-{uuid.uuid4().hex[:8]}",
            modality="text",
            content=cleaned,
            source=source_label,
            metadata={
                "source": source_label,
                "word_count": len(cleaned.split()),
                "char_count": len(cleaned)
            }
        )
