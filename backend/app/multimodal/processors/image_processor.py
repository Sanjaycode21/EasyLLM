import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from app.multimodal.schemas import NormalizedInput, VisionAnalysis
from app.multimodal.providers.vision import get_vision_provider, VisionProvider

class ImageProcessor:
    """
    Processes images (.png, .jpg, .jpeg, .webp) through Vision and OCR provider abstractions.
    Transforms visual information and embedded text into structured normalized representations.
    """
    @staticmethod
    async def process_file(file_path: Path, provider: Optional[VisionProvider] = None) -> NormalizedInput:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        vision_provider = provider or get_vision_provider()
        analysis: VisionAnalysis = await vision_provider.analyze_image(file_path)

        # Formulate normalized content
        sections = []
        if analysis.description:
            sections.append(f"[Visual Content & Scene Analysis]\n{analysis.description}")
        if analysis.extracted_text and analysis.extracted_text != analysis.description:
            sections.append(f"[OCR Extracted Text]\n{analysis.extracted_text}")

        normalized_content = "\n\n".join(sections) if sections else analysis.description or "Image content processed."

        return NormalizedInput(
            id=f"norm-img-{uuid.uuid4().hex[:8]}",
            modality="image",
            content=normalized_content.strip(),
            source=file_path.name,
            metadata={
                "filename": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "provider": analysis.provider,
                "has_text": analysis.has_text,
                "structured_data": analysis.structured_data
            }
        )
