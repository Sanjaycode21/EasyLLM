from pathlib import Path
from typing import List, Dict, Any
import pymupdf as fitz

class PDFExtractor:
    """
    Extracts text and page metadata from PDF documents using PyMuPDF.
    Zero fabrication: extracts genuine page text.
    """
    @staticmethod
    def extract_text_with_pages(file_path: Path) -> List[Dict[str, Any]]:
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        doc = fitz.open(file_path)
        pages_content = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages_content.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                    "word_count": len(text.split())
                })
        doc.close()
        return pages_content

    @staticmethod
    def extract_full_text(file_path: Path) -> str:
        pages = PDFExtractor.extract_text_with_pages(file_path)
        return "\n\n".join([f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages])
