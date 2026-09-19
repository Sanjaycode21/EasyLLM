import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any

class DOCXExtractor:
    """
    Extracts text, paragraphs, and sections from Microsoft Word (.docx) documents
    using Python standard library (zipfile + XML parser) without external dependencies.
    """
    @staticmethod
    def extract_text(file_path: Path) -> str:
        paragraphs = DOCXExtractor.extract_paragraphs(file_path)
        return "\n\n".join([p["text"] for p in paragraphs if p.get("text")])

    @staticmethod
    def extract_paragraphs(file_path: Path) -> List[Dict[str, Any]]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX file not found at: {file_path}")

        try:
            with zipfile.ZipFile(file_path) as z:
                xml_content = z.read("word/document.xml")
        except Exception as e:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                return [{"index": i + 1, "text": l, "word_count": len(l.split())} for i, l in enumerate(lines)]
            except Exception:
                raise ValueError(f"Failed to parse Word document: {str(e)}")

        tree = ET.fromstring(xml_content)
        
        paragraphs = []
        p_index = 1
        
        for p in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
            texts = [node.text for node in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text]
            full_p = "".join(texts).strip()
            if full_p:
                paragraphs.append({
                    "index": p_index,
                    "text": full_p,
                    "word_count": len(full_p.split())
                })
                p_index += 1

        return paragraphs
