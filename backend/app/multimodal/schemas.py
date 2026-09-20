from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

ModalityType = Literal["text", "document", "image", "audio", "unknown"]

class ModalityDetectionResult(BaseModel):
    modality: ModalityType
    mime_type: str
    filename: str
    extension: str
    file_size_bytes: int
    is_supported: bool
    error_message: Optional[str] = None

class NormalizedInput(BaseModel):
    id: str
    modality: ModalityType
    content: str
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PipelineTraceStep(BaseModel):
    step_id: str
    title: str
    modality: Optional[str] = None
    component: str # e.g. "Modality Detector", "PyMuPDF Extractor", "Vision/OCR Provider", "Speech-to-Text Provider", "Normalizer", "Vector Store / RAG", "Qwen3-4B Instruct"
    status: Literal["completed", "active", "failed", "pending"]
    description: str
    input_type: str
    output_type: str
    details: Optional[Dict[str, Any]] = None

class VisionAnalysis(BaseModel):
    extracted_text: str = ""
    description: str = ""
    has_text: bool = False
    provider: str
    structured_data: Dict[str, Any] = Field(default_factory=dict)

class AudioTranscript(BaseModel):
    text: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None
    provider: str
    segments: Optional[List[Dict[str, Any]]] = None

class MultimodalProcessingResult(BaseModel):
    id: str
    filename: str
    modality: ModalityType
    mime_type: str
    file_size_bytes: int
    status: Literal["PROCESSED", "FAILED", "PENDING"]
    normalized_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pipeline_trace: List[PipelineTraceStep] = Field(default_factory=list)
    error_message: Optional[str] = None

class MultimodalBatchResult(BaseModel):
    batch_id: str
    items: List[MultimodalProcessingResult]
    modalities_detected: List[str]
    total_files: int
    successful_files: int
    failed_files: int
    combined_knowledge_text: str
    pipeline_trace: List[PipelineTraceStep]
