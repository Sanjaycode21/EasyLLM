import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.config import settings
from app.api.schemas import (
    DatasetMetadata, ArchitectureAnalysis, BuildConfiguration, BuildJobStatus,
    RegisteredModel, ModelEvaluation, ChatRequest, ChatResponse, HardwareStatus
)
from app.architect.data_analyzer import DataAnalyzer
from app.architect.requirement_analyzer import RequirementAnalyzer
from app.architect.decision_engine import ArchitectureDecisionEngine
from app.training.hardware_check import get_hardware_status
from app.compute.provider import compute_provider
from app.jobs.job_manager import job_manager
from app.inference.engine import InferenceEngine

router = APIRouter()

# Stored uploaded datasets map {dataset_id: Path}
uploaded_files_map = {}

@router.get("/hardware", response_model=HardwareStatus)
async def get_hardware():
    hw = get_hardware_status()
    return HardwareStatus(**hw)

@router.post("/upload", response_model=DatasetMetadata)
async def upload_dataset(file: UploadFile = File(...)):
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".docx", ".doc", ".jsonl", ".csv", ".txt", ".json"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")
    
    file_id = f"ds-{uuid.uuid4().hex[:8]}"
    saved_filename = f"{file_id}_{file.filename}"
    save_path = settings.datasets_dir / saved_filename
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    uploaded_files_map[file_id] = save_path
    
    # Analyze uploaded dataset
    metadata = DataAnalyzer.analyze_file(save_path)
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
    
    job = compute_provider.submit_job(config, dataset_path)
    return job

@router.get("/build/{job_id}", response_model=BuildJobStatus)
async def get_build_status(job_id: str):
    job = compute_provider.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

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
