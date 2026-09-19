import sys
import asyncio
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion.pdf_extractor import PDFExtractor
from app.ingestion.dataset_processor import DatasetProcessor
from app.architect.data_analyzer import DataAnalyzer
from app.architect.requirement_analyzer import RequirementAnalyzer
from app.architect.decision_engine import ArchitectureDecisionEngine
from app.rag.chunker import DocumentChunker
from app.rag.vector_store import VectorStore
from app.evaluation.evaluator import SystemEvaluator
from app.evaluation.metrics import EvaluationMetrics

async def test_end_to_end():
    print("=== [1] Testing PDF Data Extraction & Analysis ===")
    pdf_path = Path(__file__).resolve().parent.parent.parent / "datasets" / "company_manual.pdf"
    assert pdf_path.exists(), f"PDF not found at {pdf_path}"
    
    meta_pdf = DataAnalyzer.analyze_file(pdf_path)
    print(f"PDF Analysis: {meta_pdf.filename} | pages={meta_pdf.num_records} | format={meta_pdf.format} | knowledge_density={meta_pdf.knowledge_density}")
    assert meta_pdf.file_type == "pdf"
    assert meta_pdf.num_records >= 2
    assert meta_pdf.training_compatible is False

    print("\n=== [2] Testing JSONL Dataset Validation ===")
    jsonl_path = Path(__file__).resolve().parent.parent.parent / "datasets" / "sample_support_chat.jsonl"
    assert jsonl_path.exists(), f"JSONL not found at {jsonl_path}"
    
    meta_jsonl = DataAnalyzer.analyze_file(jsonl_path)
    print(f"JSONL Analysis: {meta_jsonl.filename} | records={meta_jsonl.num_records} | valid={meta_jsonl.num_valid_examples} | format={meta_jsonl.format} | training_compat={meta_jsonl.training_compatible}")
    assert meta_jsonl.file_type == "jsonl"
    assert meta_jsonl.num_valid_examples >= 5
    assert meta_jsonl.training_compatible is True

    print("\n=== [3] Testing Requirement Analyzer & Decision Engine ===")
    # Case A: Knowledge Retrieval requirement
    req_rag = "Build an AI that answers customer questions using our company manual."
    analysis_rag = await RequirementAnalyzer.analyze(req_rag, meta_pdf)
    final_rag = ArchitectureDecisionEngine.resolve_architecture(analysis_rag, meta_pdf)
    print(f"Decision for RAG: strategy={final_rag.recommended_strategy} | reason={final_rag.reason}")
    assert final_rag.recommended_strategy == "rag"

    # Case B: Style / Behavioral customization
    req_qlora = "Create a customer support bot that writes polite, professional responses following our dataset examples."
    analysis_qlora = await RequirementAnalyzer.analyze(req_qlora, meta_jsonl)
    final_qlora = ArchitectureDecisionEngine.resolve_architecture(analysis_qlora, meta_jsonl)
    print(f"Decision for QLoRA: strategy={final_qlora.recommended_strategy} | reason={final_qlora.reason}")
    assert final_qlora.recommended_strategy == "qlora"

    # Case C: Hybrid requirement
    req_hybrid = "Create an AI that answers using our company policies and responds in our support team's tone and style."
    analysis_hybrid = await RequirementAnalyzer.analyze(req_hybrid, meta_jsonl)
    final_hybrid = ArchitectureDecisionEngine.resolve_architecture(analysis_hybrid, meta_jsonl)
    print(f"Decision for Hybrid: strategy={final_hybrid.recommended_strategy} | reason={final_hybrid.reason}")
    assert final_hybrid.recommended_strategy == "hybrid"

    print("\n=== [4] Testing RAG Ingestion & Vector Retrieval ===")
    pages = PDFExtractor.extract_text_with_pages(pdf_path)
    chunks = DocumentChunker.chunk_pages(pages, chunk_size=300, chunk_overlap=40, doc_name="company_manual.pdf")
    print(f"Extracted {len(chunks)} chunks from PDF.")
    
    test_index_id = "test-vector-index"
    vs = VectorStore(test_index_id)
    vs.add_documents(chunks)
    
    query = "What is the return and refund policy timeframe?"
    results = vs.search(query, top_k=2)
    print(f"Search Query: '{query}' -> Retrieved {len(results)} results:")
    for chunk, score in results:
        print(f"  - Score: {score:.3f} | Snippet: {chunk['text'][:100]}...")
    assert len(results) > 0
    assert any("30-day" in r[0]["text"] or "refund" in r[0]["text"].lower() for r in results)

    print("\n=== [5] Testing Automated Evaluator & Metrics ===")
    val_records = [{"messages": [{"role": "user", "content": "How do I return a product?"}, {"role": "assistant", "content": "Orders returned within 30 days are eligible for a 100% refund."}]}]
    eval_report = await SystemEvaluator.evaluate_model("test-model", val_records, req_rag)
    print(f"Evaluation Score: Base={eval_report.overall_base_score}% | Custom={eval_report.overall_custom_score}%")
    assert eval_report.overall_custom_score > eval_report.overall_base_score

    print("\n[SUCCESS] ALL CORE PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
