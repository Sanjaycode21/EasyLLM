import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.evaluation.schemas import EvaluationReport, EvaluationJobStatus, EvaluationDataset
from app.evaluation.manager import evaluation_manager
from app.evaluation.splitter import EvaluationDatasetSplitter
from app.api.schemas import (
    DatasetMetadata, ArchitectureAnalysis, BuildConfiguration, BuildJobStatus,
    RegisteredModel, ModelEvaluation, ChatRequest, ChatResponse, HardwareStatus,
    EvaluationRunRequest
)
from app.ingestion.dataset_processor import DatasetProcessor
from app.rag.chunker import DocumentChunker
from app.ingestion.pdf_extractor import PDFExtractor
from app.ingestion.docx_extractor import DOCXExtractor


from app.architect.data_analyzer import DataAnalyzer
from app.architect.requirement_analyzer import RequirementAnalyzer
from app.architect.decision_engine import ArchitectureDecisionEngine
from app.training.hardware_check import get_hardware_status
from app.compute.provider import get_compute_provider
from app.jobs.job_manager import job_manager
from app.inference.engine import InferenceEngine

from app.multimodal.pipeline import MultimodalPipeline
from app.multimodal.schemas import MultimodalProcessingResult, MultimodalBatchResult

router = APIRouter()

# Stored uploaded datasets map {dataset_id: Path}
uploaded_files_map = {}

@router.get("/hardware", response_model=HardwareStatus)
@router.get("/diagnostics", response_model=HardwareStatus)
async def get_hardware():
    hw = get_hardware_status()
    return HardwareStatus(**hw)

@router.post("/multimodal/process", response_model=MultimodalBatchResult)
async def process_multimodal(files: List[UploadFile] = File(...)):
    saved_paths = []
    for f in files:
        file_id = f"mm-{uuid.uuid4().hex[:8]}"
        saved_filename = f"{file_id}_{f.filename}"
        save_path = settings.datasets_dir / saved_filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved_paths.append(save_path)
        uploaded_files_map[file_id] = save_path

    batch_result = await MultimodalPipeline.process_batch(saved_paths)
    return batch_result

@router.post("/upload", response_model=DatasetMetadata)
async def upload_dataset(file: UploadFile = File(...)):
    file_ext = Path(file.filename).suffix.lower()
    allowed_extensions = [
        ".pdf", ".docx", ".doc", ".jsonl", ".csv", ".txt", ".json", ".md",
        ".png", ".jpg", ".jpeg", ".webp",
        ".wav", ".mp3", ".m4a"
    ]
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}. Supported: Text (.txt, .jsonl, .csv), Documents (.pdf, .docx), Images (.png, .jpg, .webp), Audio (.wav, .mp3, .m4a).")
    
    file_id = f"ds-{uuid.uuid4().hex[:8]}"
    saved_filename = f"{file_id}_{file.filename}"
    save_path = settings.datasets_dir / saved_filename
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    uploaded_files_map[file_id] = save_path
    
    # Process through Multimodal Pipeline
    mm_result = await MultimodalPipeline.process_file(save_path)
    
    # Analyze uploaded dataset metadata
    metadata = DataAnalyzer.analyze_file(save_path)
    metadata.modality = mm_result.modality
    metadata.normalized_content = mm_result.normalized_content
    metadata.pipeline_trace = mm_result.pipeline_trace
    
    if mm_result.status == "FAILED" and mm_result.error_message:
        metadata.validation_errors.append(mm_result.error_message)

    return metadata

@router.post("/analyze", response_model=ArchitectureAnalysis)
async def analyze_architecture(
    requirement: str = Form(...),
    dataset_id: Optional[str] = Form(None)
):
    dataset_metadata = None
    if dataset_id and dataset_id in uploaded_files_map:
        file_path = uploaded_files_map[dataset_id]
        dataset_metadata = DataAnalyzer.analyze_file(file_path)
    
    # 1. Requirement Analysis
    req_analysis = await RequirementAnalyzer.analyze(requirement, dataset_metadata)
    
    # 2. Decision Engine Fusion & Validation
    final_decision = ArchitectureDecisionEngine.resolve_architecture(req_analysis, dataset_metadata)
    return final_decision

@router.post("/build", response_model=BuildJobStatus)
async def start_build(config: BuildConfiguration):
    dataset_path = None
    if config.dataset_id and config.dataset_id in uploaded_files_map:
        dataset_path = uploaded_files_map[config.dataset_id]
    
    provider = get_compute_provider(
        strategy=config.strategy,
        force_provider=config.force_compute_provider if config.force_compute_provider != "auto" else None
    )
    job = provider.submit_job(config, dataset_path)
    return job

@router.get("/build/{job_id}", response_model=BuildJobStatus)
async def get_build_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

@router.get("/compute/colab/{job_id}")
async def download_colab_notebook(job_id: str):
    nb_filename = f"EasyLLM_Qwen3_4B_QLoRA_{job_id[:8]}.ipynb"
    nb_path = settings.artifacts_dir / nb_filename
    if not nb_path.exists():
        raise HTTPException(status_code=404, detail=f"Colab notebook for job {job_id} not found.")
    return FileResponse(
        path=nb_path,
        filename=nb_filename,
        media_type="application/x-ipynb+json"
    )

@router.get("/models", response_model=List[RegisteredModel])
async def list_models():
    return list(job_manager.models.values())

@router.get("/models/{model_id}", response_model=RegisteredModel)
async def get_model(model_id: str):
    model = job_manager.models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return model

@router.get("/evaluation/{model_id}", response_model=ModelEvaluation)
async def get_evaluation(model_id: str):
    model = job_manager.models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    if not model.evaluation:
        raise HTTPException(status_code=404, detail=f"Evaluation pending or not found for model {model_id}")
    return model.evaluation

@router.get("/evaluation/report/{id_or_model_id}", response_model=EvaluationReport)
async def get_evaluation_report(id_or_model_id: str):
    # Check if direct eval_id in evaluation_manager
    report = evaluation_manager.get_report(id_or_model_id)
    if report:
        return report

    # Check if it's a model_id with registered evaluation_report
    model = job_manager.models.get(id_or_model_id)
    if model and model.evaluation_report:
        return model.evaluation_report

    # Check if there are evaluations listed for this pipeline
    evals = evaluation_manager.list_evaluations_for_pipeline(id_or_model_id)
    if evals:
        return evals[0]

    raise HTTPException(
        status_code=404,
        detail=f"Evaluation report not found for '{id_or_model_id}'. Evaluation unavailable: no valid held-out dataset."
    )

@router.get("/pipelines/{pipeline_id}/evaluations", response_model=List[EvaluationReport])
async def list_pipeline_evaluations(pipeline_id: str):
    evals = evaluation_manager.list_evaluations_for_pipeline(pipeline_id)
    if not evals:
        model = job_manager.models.get(pipeline_id)
        if model and model.evaluation_report:
            return [model.evaluation_report]
    return evals

@router.post("/evaluation/run", response_model=EvaluationJobStatus)
async def run_evaluation_job(request: EvaluationRunRequest):
    model = job_manager.models.get(request.pipeline_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Pipeline/Model {request.pipeline_id} not found")

    dataset_path = None
    if request.dataset_id and request.dataset_id in uploaded_files_map:
        dataset_path = uploaded_files_map[request.dataset_id]

    # Create held-out evaluation dataset
    eval_dataset: Optional[EvaluationDataset] = None
    if dataset_path and dataset_path.suffix.lower() in [".jsonl", ".csv"]:
        records, _ = DatasetProcessor.validate_and_parse_jsonl(dataset_path) if dataset_path.suffix.lower() == ".jsonl" else DatasetProcessor.parse_csv_to_chat(dataset_path)
        if records:
            _, eval_dataset = EvaluationDatasetSplitter.split_records(records, dataset_name=dataset_path.name, eval_ratio=request.split_ratio, seed=request.seed)
    elif dataset_path and dataset_path.suffix.lower() in [".pdf", ".docx", ".doc", ".txt"]:
        if dataset_path.suffix.lower() == ".pdf":
            pages = PDFExtractor.extract_text_with_pages(dataset_path)
            chunks = DocumentChunker.chunk_pages(pages, chunk_size=500, chunk_overlap=50, doc_name=dataset_path.name)
        elif dataset_path.suffix.lower() in [".docx", ".doc"]:
            text = DOCXExtractor.extract_text(dataset_path)
            chunks = DocumentChunker.chunk_text(text, chunk_size=500, chunk_overlap=50, metadata={"document_name": dataset_path.name})
        else:
            with open(dataset_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            chunks = DocumentChunker.chunk_text(text, chunk_size=500, chunk_overlap=50, metadata={"document_name": dataset_path.name})
        if chunks:
            eval_dataset = EvaluationDatasetSplitter.create_document_eval_set(chunks, doc_name=dataset_path.name, eval_ratio=request.split_ratio, seed=request.seed)

    if not eval_dataset or not eval_dataset.examples:
        # Fallback to existing model's evaluation samples if available
        if model.evaluation_report and model.evaluation_report.sample_comparisons:
            from app.evaluation.schemas import EvaluationExample
            eval_dataset = EvaluationDataset(
                dataset_id=f"eval-ds-{request.pipeline_id}",
                dataset_name=model.dataset_name or "evaluation_benchmark",
                total_examples=len(model.evaluation_report.sample_comparisons),
                train_examples_count=0,
                eval_examples_count=len(model.evaluation_report.sample_comparisons),
                examples=[
                    EvaluationExample(
                        id=f"ex-{i+1}",
                        prompt=s.prompt,
                        expected_output=s.expected_output
                    )
                    for i, s in enumerate(model.evaluation_report.sample_comparisons)
                ]
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Evaluation unavailable: no valid held-out dataset could be extracted."
            )

    job = evaluation_manager.create_job(request.pipeline_id)
    
    # Run evaluation in background task
    import asyncio
    asyncio.create_task(evaluation_manager.run_evaluation_async(
        eval_id=job.evaluation_id,
        pipeline_info=model.model_dump(),
        eval_dataset=eval_dataset
    ))

    return job

@router.get("/evaluation/job/{eval_id}", response_model=EvaluationJobStatus)
async def get_evaluation_job(eval_id: str):
    job = evaluation_manager.get_job(eval_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Evaluation job {eval_id} not found")
    return job

@router.get("/evaluation/{eval_id}/comparison")
async def get_evaluation_comparison(eval_id: str):
    report = evaluation_manager.get_report(eval_id)
    if not report:
        # Try finding in registered models
        model = job_manager.models.get(eval_id)
        if model and model.evaluation_report:
            report = model.evaluation_report
        else:
            raise HTTPException(status_code=404, detail=f"Evaluation report {eval_id} not found")

    return {
        "evaluation_id": report.evaluation_id,
        "pipeline_id": report.pipeline_id,
        "overall_status": report.overall_status,
        "overall_absolute_change_pp": report.overall_absolute_change_pp,
        "overall_relative_change_pct": report.overall_relative_change_pct,
        "metrics": report.metrics,
        "sample_comparisons": report.sample_comparisons,
        "system_performance": report.system_performance,
        "conclusion": report.conclusion
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_model(request: ChatRequest):
    model = job_manager.models.get(request.model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {request.model_id} not found")
    
    response = await InferenceEngine.generate_response(
        model_id=request.model_id,
        message=request.message,
        model_info=model.model_dump(),
        history=request.history
    )
    return response

