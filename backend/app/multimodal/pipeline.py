import uuid
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.multimodal.schemas import (
    ModalityType,
    NormalizedInput,
    PipelineTraceStep,
    MultimodalProcessingResult,
    MultimodalBatchResult
)
from app.multimodal.detector import ModalityDetector
from app.multimodal.processors.text_processor import TextProcessor
from app.multimodal.processors.document_processor import DocumentProcessor
from app.multimodal.processors.image_processor import ImageProcessor
from app.multimodal.processors.audio_processor import AudioProcessor
from app.multimodal.providers.vision import VisionProvider
from app.multimodal.providers.speech import SpeechProvider

class MultimodalPipeline:
    """
    Central Multimodal Pipeline Orchestrator.
    Routes heterogeneous inputs through deterministic detection, modality processors,
    and unifies them into NormalizedInput representation with a comprehensive pipeline trace.
    """
    @staticmethod
    async def process_file(
        file_path: Path,
        vision_provider: Optional[VisionProvider] = None,
        speech_provider: Optional[SpeechProvider] = None
    ) -> MultimodalProcessingResult:
        file_path = Path(file_path)
        item_id = f"proc-{uuid.uuid4().hex[:8]}"
        trace: List[PipelineTraceStep] = []

        # 1. Modality Detection Step
        detection = ModalityDetector.detect_file(file_path)
        
        trace.append(PipelineTraceStep(
            step_id="step-1-detect",
            title="1. Modality Detection",
            modality=detection.modality,
            component="Deterministic Modality Detector",
            status="completed" if detection.is_supported else "failed",
            description=f"Identified modality '{detection.modality.upper()}' from extension '{detection.extension}' ({detection.mime_type}).",
            input_type=f"Binary File ({detection.extension})",
            output_type=f"Modality ({detection.modality})",
            details={
                "mime_type": detection.mime_type,
                "file_size_bytes": detection.file_size_bytes,
                "is_supported": detection.is_supported
            }
        ))

        if not detection.is_supported:
            return MultimodalProcessingResult(
                id=item_id,
                filename=file_path.name,
                modality="unknown",
                mime_type=detection.mime_type,
                file_size_bytes=detection.file_size_bytes,
                status="FAILED",
                error_message=detection.error_message,
                pipeline_trace=trace
            )

        # 2. Modality-Specific Processing & Extraction
        normalized: Optional[NormalizedInput] = None
        error_msg: Optional[str] = None
        processor_name = ""

        try:
            if detection.modality == "text":
                processor_name = "Text Normalizer"
                normalized = TextProcessor.process_file(file_path)

            elif detection.modality == "document":
                processor_name = "PyMuPDF / Word Document Extractor"
                normalized = DocumentProcessor.process_file(file_path)

            elif detection.modality == "image":
                processor_name = "Vision & OCR Provider"
                normalized = await ImageProcessor.process_file(file_path, provider=vision_provider)

            elif detection.modality == "audio":
                processor_name = "Speech-to-Text Transcriber"
                normalized = await AudioProcessor.process_file(file_path, provider=speech_provider)

            trace.append(PipelineTraceStep(
                step_id="step-2-process",
                title=f"2. {detection.modality.capitalize()} Preprocessing & Feature Extraction",
                modality=detection.modality,
                component=processor_name,
                status="completed",
                description=f"Extracted content using {processor_name}.",
                input_type=f"{detection.modality.capitalize()} Stream",
                output_type="Extracted Text / Semantics",
                details=normalized.metadata if normalized else {}
            ))

            # 3. Normalization Step
            trace.append(PipelineTraceStep(
                step_id="step-3-normalize",
                title="3. Unified Normalization",
                modality=detection.modality,
                component="Representation Normalizer",
                status="completed",
                description=f"Normalized {len(normalized.content.split())} words into standard schema for RAG / QLoRA.",
                input_type="Raw Extracted Text",
                output_type="NormalizedInput Record",
                details={"normalized_id": normalized.id, "char_count": len(normalized.content)}
            ))

            return MultimodalProcessingResult(
                id=item_id,
                filename=file_path.name,
                modality=detection.modality,
                mime_type=detection.mime_type,
                file_size_bytes=detection.file_size_bytes,
                status="PROCESSED",
                normalized_content=normalized.content,
                metadata=normalized.metadata,
                pipeline_trace=trace
            )

        except Exception as e:
            error_msg = str(e)
            trace.append(PipelineTraceStep(
                step_id="step-2-process",
                title=f"2. {detection.modality.capitalize()} Preprocessing",
                modality=detection.modality,
                component=processor_name or "Modality Processor",
                status="failed",
                description=f"Processing failed: {error_msg}",
                input_type=f"{detection.modality.capitalize()} Stream",
                output_type="None",
                details={"error": error_msg}
            ))
            return MultimodalProcessingResult(
                id=item_id,
                filename=file_path.name,
                modality=detection.modality,
                mime_type=detection.mime_type,
                file_size_bytes=detection.file_size_bytes,
                status="FAILED",
                error_message=error_msg,
                pipeline_trace=trace
            )

    @staticmethod
    async def process_batch(
        file_paths: List[Path],
        vision_provider: Optional[VisionProvider] = None,
        speech_provider: Optional[SpeechProvider] = None
    ) -> MultimodalBatchResult:
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"
        results: List[MultimodalProcessingResult] = []

        for p in file_paths:
            res = await MultimodalPipeline.process_file(p, vision_provider, speech_provider)
            results.append(res)

        modalities = sorted(list(set(r.modality for r in results if r.status == "PROCESSED" and r.modality != "unknown")))
        successful = [r for r in results if r.status == "PROCESSED"]
        failed = [r for r in results if r.status == "FAILED"]

        # Aggregate combined knowledge text
        combined_texts = []
        for r in successful:
            if r.normalized_content:
                combined_texts.append(f"=== [Source: {r.filename} | Modality: {r.modality.upper()}] ===\n{r.normalized_content}")

        combined_knowledge = "\n\n".join(combined_texts)

        # Build aggregated master pipeline trace
        master_trace: List[PipelineTraceStep] = []
        
        # Step A: Ingestion & Detection
        master_trace.append(PipelineTraceStep(
            step_id="trace-ingest",
            title="1. Multimodal Intake & Routing",
            component="Deterministic Modality Router",
            status="completed" if successful else "failed",
            description=f"Received {len(file_paths)} files across modalities: {', '.join(modalities) if modalities else 'None'}.",
            input_type="Multi-format Raw Files",
            output_type=f"Detected Modalities: {modalities}"
        ))

        # Step B: Parallel Modality Transformation
        master_trace.append(PipelineTraceStep(
            step_id="trace-transform",
            title="2. Modality-Specific Feature & Content Extraction",
            component="PyMuPDF / Word XML / Vision OCR / Speech Transcriber",
            status="completed" if successful else "failed",
            description=f"Successfully extracted knowledge from {len(successful)}/{len(file_paths)} files.",
            input_type="Heterogeneous Binary Payloads",
            output_type="Normalized Domain Content"
        ))

        # Step C: Canonical Representation
        master_trace.append(PipelineTraceStep(
            step_id="trace-normalize",
            title="3. Canonical Knowledge Normalization",
            component="Unified Schema Normalizer",
            status="completed",
            description=f"Synthesized {len(combined_knowledge.split())} words into unified context representation.",
            input_type="Raw Extracted Documents & Media",
            output_type="Vector-Ready Context Chunks"
        ))

        return MultimodalBatchResult(
            batch_id=batch_id,
            items=results,
            modalities_detected=modalities,
            total_files=len(file_paths),
            successful_files=len(successful),
            failed_files=len(failed),
            combined_knowledge_text=combined_knowledge,
            pipeline_trace=master_trace
        )
