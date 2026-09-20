import uuid
from pathlib import Path
from typing import Dict, Any, List
from app.multimodal.schemas import NormalizedInput
from app.ingestion.pdf_extractor import PDFExtractor
from app.ingestion.docx_extractor import DOCXExtractor

class DocumentProcessor:
    """
    Extracts text and hierarchical structure from documents (.pdf, .docx).
    Integrates directly with PyMuPDF and Word parsers, preserving page metadata.
    """
    @staticmethod
    def process_file(file_path: Path) -> NormalizedInput:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        ext = file_path.suffix.lower()
        content = ""
        metadata: Dict[str, Any] = {
            "filename": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "document_type": ext.lstrip(".")
        }

        if ext == ".pdf":
            pages_data = PDFExtractor.extract_text_with_pages(file_path)
            metadata["num_pages"] = len(pages_data)
            metadata["pages"] = [{"page_number": p["page_number"], "char_count": p["char_count"]} for p in pages_data]
            content = PDFExtractor.extract_full_text(file_path)

        elif ext in [".docx", ".doc"]:
            paragraphs = DOCXExtractor.extract_paragraphs(file_path)
            metadata["num_paragraphs"] = len(paragraphs)
            content = DOCXExtractor.extract_text(file_path)

        else:
            raise ValueError(f"Unsupported document format: {ext}")

        return NormalizedInput(
            id=f"norm-doc-{uuid.uuid4().hex[:8]}",
            modality="document",
            content=content.strip(),
            source=file_path.name,
            metadata=metadata
        )
