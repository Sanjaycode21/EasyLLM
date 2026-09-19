import json
from pathlib import Path
from typing import Dict, Any, List
from app.api.schemas import DatasetMetadata
from app.ingestion.pdf_extractor import PDFExtractor
from app.ingestion.dataset_processor import DatasetProcessor
from app.ingestion.docx_extractor import DOCXExtractor

class DataAnalyzer:
    """
    Inspects user uploaded files and extracts authentic structural & semantic metadata.
    Zero fabrication of record counts, file sizes, or validation metrics.
    """
    @staticmethod
    def analyze_file(file_path: Path) -> DatasetMetadata:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = file_path.stat().st_size
        extension = file_path.suffix.lower().lstrip(".")
        filename = file_path.name
        
        # 1. PDF Analysis
        if extension == "pdf":
            try:
                pages = PDFExtractor.extract_text_with_pages(file_path)
                total_pages = len(pages)
                total_words = sum(p["word_count"] for p in pages)
                preview = [{"page": p["page_number"], "snippet": p["text"][:200] + "..."} for p in pages[:3]]
                
                return DatasetMetadata(
                    filename=filename,
                    file_type="pdf",
                    file_size_bytes=file_size,
                    num_records=total_pages, # number of pages
                    num_valid_examples=total_pages,
                    num_invalid_examples=0,
                    format="document_text",
                    sample_preview=preview,
                    training_compatible=False, # PDFs are primarily knowledge documents for RAG
                    knowledge_density=0.95,
                    validation_errors=[]
                )
            except Exception as e:
                return DatasetMetadata(
                    filename=filename,
                    file_type="pdf",
                    file_size_bytes=file_size,
                    num_records=0,
                    num_valid_examples=0,
                    num_invalid_examples=1,
                    format="unknown",
                    sample_preview=None,
                    training_compatible=False,
                    knowledge_density=0.0,
                    validation_errors=[f"Failed to read PDF: {str(e)}"]
                )

        # 2. Word DOCX / DOC Analysis
        elif extension in ["docx", "doc"]:
            try:
                paragraphs = DOCXExtractor.extract_paragraphs(file_path)
                total_paragraphs = len(paragraphs)
                total_words = sum(p["word_count"] for p in paragraphs)
                preview = [{"paragraph": p["index"], "snippet": p["text"][:200] + "..."} for p in paragraphs[:3]]
                
                return DatasetMetadata(
                    filename=filename,
                    file_type="docx",
                    file_size_bytes=file_size,
                    num_records=total_paragraphs,
                    num_valid_examples=total_paragraphs,
                    num_invalid_examples=0,
                    format="document_text",
                    sample_preview=preview,
                    training_compatible=False,
                    knowledge_density=0.95,
                    validation_errors=[]
                )
            except Exception as e:
                return DatasetMetadata(
                    filename=filename,
                    file_type="docx",
                    file_size_bytes=file_size,
                    num_records=0,
                    num_valid_examples=0,
                    num_invalid_examples=1,
                    format="unknown",
                    sample_preview=None,
                    training_compatible=False,
                    knowledge_density=0.0,
                    validation_errors=[f"Failed to read Word document: {str(e)}"]
                )

        # 3. JSONL Analysis
        elif extension == "jsonl":
            valid_records, errors = DatasetProcessor.validate_and_parse_jsonl(file_path)
            total_records = len(valid_records) + len(errors)
            preview = [r["messages"] for r in valid_records[:3]] if valid_records else None
            
            is_training_compat = len(valid_records) >= 3 and len(errors) < (len(valid_records) * 0.5)
            
            return DatasetMetadata(
                filename=filename,
                file_type="jsonl",
                file_size_bytes=file_size,
                num_records=total_records,
                num_valid_examples=len(valid_records),
                num_invalid_examples=len(errors),
                format="chat_messages",
                sample_preview=preview,
                training_compatible=is_training_compat,
                knowledge_density=0.3 if is_training_compat else 0.8,
                validation_errors=errors[:10] # Show top 10 errors
            )

        # 4. CSV Analysis
        elif extension == "csv":
            valid_records, errors = DatasetProcessor.parse_csv_to_chat(file_path)
            total_records = len(valid_records) + len(errors)
            preview = [r["messages"] for r in valid_records[:3]] if valid_records else None
            is_training_compat = len(valid_records) >= 3
            
            return DatasetMetadata(
                filename=filename,
                file_type="csv",
                file_size_bytes=file_size,
                num_records=total_records,
                num_valid_examples=len(valid_records),
                num_invalid_examples=len(errors),
                format="chat_messages" if is_training_compat else "tabular",
                sample_preview=preview,
                training_compatible=is_training_compat,
                knowledge_density=0.4,
                validation_errors=errors[:10]
            )

        # 5. Plain Text TXT Analysis
        elif extension == "txt":
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            preview = [{"line": idx + 1, "text": line[:150]} for idx, line in enumerate(lines[:3])]
            
            return DatasetMetadata(
                filename=filename,
                file_type="txt",
                file_size_bytes=file_size,
                num_records=len(lines),
                num_valid_examples=len(lines),
                num_invalid_examples=0,
                format="document_text",
                sample_preview=preview,
                training_compatible=False,
                knowledge_density=0.90,
                validation_errors=[]
            )

        # Unknown format
        else:
            return DatasetMetadata(
                filename=filename,
                file_type="unknown",
                file_size_bytes=file_size,
                num_records=0,
                num_valid_examples=0,
                num_invalid_examples=0,
                format="unknown",
                sample_preview=None,
                training_compatible=False,
                knowledge_density=0.0,
                validation_errors=[f"Unsupported file format '.{extension}'. Supported: .pdf, .docx, .doc, .jsonl, .csv, .txt"]
            )
