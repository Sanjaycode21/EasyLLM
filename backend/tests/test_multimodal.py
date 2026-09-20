import sys
import asyncio
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.multimodal.detector import ModalityDetector
from app.multimodal.processors.text_processor import TextProcessor
from app.multimodal.processors.document_processor import DocumentProcessor
from app.multimodal.pipeline import MultimodalPipeline
from app.multimodal.providers.vision import get_vision_provider, VisionProviderError
from app.multimodal.providers.speech import get_speech_provider, SpeechProviderError
from app.rag.chunker import DocumentChunker
from app.rag.vector_store import VectorStore

async def test_multimodal_module():
    print("=== [1] Testing Modality Detector ===")
    datasets_dir = Path(__file__).resolve().parent.parent.parent / "datasets"
    
    # 1.1 Text
    txt_res = ModalityDetector.detect_file(Path("sample_test.txt"))
    print(f"TXT Detection: modality={txt_res.modality} | mime={txt_res.mime_type} | supported={txt_res.is_supported}")
    assert txt_res.modality == "text"
    assert txt_res.is_supported is True

    # 1.2 Document
    pdf_res = ModalityDetector.detect_file(datasets_dir / "company_manual.pdf")
    print(f"PDF Detection: modality={pdf_res.modality} | mime={pdf_res.mime_type} | supported={pdf_res.is_supported}")
    assert pdf_res.modality == "document"
    assert pdf_res.is_supported is True

    # 1.3 Image
    img_res = ModalityDetector.detect_file(Path("architecture_diagram.png"))
    print(f"Image Detection: modality={img_res.modality} | mime={img_res.mime_type} | supported={img_res.is_supported}")
    assert img_res.modality == "image"
    assert img_res.is_supported is True

    # 1.4 Audio
    aud_res = ModalityDetector.detect_file(Path("customer_call.mp3"))
    print(f"Audio Detection: modality={aud_res.modality} | mime={aud_res.mime_type} | supported={aud_res.is_supported}")
    assert aud_res.modality == "audio"
    assert aud_res.is_supported is True

    # 1.5 Unsupported File Format (Deterministic Rejection)
    unsupported_res = ModalityDetector.detect_file(Path("malicious_script.exe"))
    print(f"Unsupported Detection: modality={unsupported_res.modality} | supported={unsupported_res.is_supported} | err={unsupported_res.error_message}")
    assert unsupported_res.modality == "unknown"
    assert unsupported_res.is_supported is False
    assert "Unsupported format" in unsupported_res.error_message

    print("\n=== [2] Testing Text Processor & Sanitization ===")
    raw_dirty_text = "Acme Return Policy\r\n\x00\x08All items returned within 30 days are 100% refunded.\n\nThank you!"
    normalized_txt = TextProcessor.process_string(raw_dirty_text, "test_policy")
    print(f"Normalized Text Content:\n{normalized_txt.content}")
    assert "\x00" not in normalized_txt.content
    assert "\r" not in normalized_txt.content
    assert "30 days" in normalized_txt.content
    assert normalized_txt.modality == "text"

    print("\n=== [3] Testing Document Processor (PyMuPDF) ===")
    pdf_path = datasets_dir / "company_manual.pdf"
    if pdf_path.exists():
        normalized_doc = DocumentProcessor.process_file(pdf_path)
        print(f"Extracted Document: {normalized_doc.source} | words={normalized_doc.metadata.get('num_pages')} pages | chars={len(normalized_doc.content)}")
        assert normalized_doc.modality == "document"
        assert len(normalized_doc.content) > 50

    print("\n=== [4] Testing Provider Abstractions & Zero-Fake-Data Enforcement ===")
    # Vision Provider error or execution check
    try:
        vp = get_vision_provider()
        print(f"Vision provider active: {type(vp).__name__}")
    except VisionProviderError as e:
        print(f"Vision provider correctly enforced unconfigured credential notice: {e}")
        assert "No Vision Provider configured" in str(e)

    # Speech Provider error or execution check
    try:
        sp = get_speech_provider()
        print(f"Speech provider active: {type(sp).__name__}")
    except SpeechProviderError as e:
        print(f"Speech provider correctly enforced unconfigured credential notice: {e}")
        assert "No Speech-to-Text Provider configured" in str(e)

    print("\n=== [5] Testing Multimodal Batch Processing & Trace Generation ===")
    test_batch_paths = [pdf_path]
    batch_res = await MultimodalPipeline.process_batch(test_batch_paths)
    print(f"Batch Processed: {batch_res.successful_files}/{batch_res.total_files} successful | modalities={batch_res.modalities_detected}")
    assert batch_res.total_files == 1
    assert batch_res.successful_files == 1
    assert "document" in batch_res.modalities_detected
    assert len(batch_res.pipeline_trace) >= 3

    print("\n=== [6] Testing Multimodal RAG Ingestion & Vector Retrieval ===")
    mm_chunks = DocumentChunker.chunk_text(
        batch_res.combined_knowledge_text,
        chunk_size=300,
        chunk_overlap=40,
        metadata={"document_name": "company_manual.pdf", "modality": "document"}
    )
    mm_vector_store = VectorStore("test-mm-vector-store")
    mm_vector_store.add_documents(mm_chunks)
    
    search_query = "What is the warranty and uptime guarantee?"
    results = mm_vector_store.search(search_query, top_k=2)
    print(f"Query '{search_query}' retrieved {len(results)} chunks:")
    for chunk, score in results:
        print(f"  - Score: {score:.3f} | Text: {chunk['text'][:90]}...")
    assert len(results) > 0

    print("\n[SUCCESS] ALL MULTIMODAL ACCEPTANCE TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_multimodal_module())
