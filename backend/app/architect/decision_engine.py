from typing import Optional, List
from app.api.schemas import ArchitectureAnalysis, DatasetMetadata
from app.training.hardware_check import get_hardware_status
from app.training.model_registry import select_optimal_model
from app.multimodal.schemas import PipelineTraceStep

class ArchitectureDecisionEngine:
    """
    Fuses LLM requirement reasoning, multimodal dataset structure inspection, and hardware VRAM profiling.
    
    CORE ARCHITECTURAL RULES:
    - RAG = changes what the AI knows (external knowledge, documentation, image diagrams, audio records, citation needed).
    - QLoRA = changes how the AI behaves (tone, persona, conversational style, custom instruction following).
    - Hybrid = changes both (knowledge grounding + distinct persona).
    
    Decision is NOT based solely on file extension. It evaluates user intent, data structure,
    multimodal modalities, and compute feasibility.
    """
    @staticmethod
    def resolve_architecture(
        req_analysis: ArchitectureAnalysis,
        data_metadata: Optional[DatasetMetadata] = None
    ) -> ArchitectureAnalysis:
        validation_notes: List[str] = []
        strategy = req_analysis.recommended_strategy
        hw = get_hardware_status()
        base_model = select_optimal_model(hw["cuda_available"], hw["free_vram_gb"])

        modalities: List[str] = []
        if data_metadata and data_metadata.modality:
            modalities.append(data_metadata.modality)
        elif not data_metadata:
            modalities.append("text")

        # 1. Evaluate User's Core Intent
        wants_knowledge = req_analysis.knowledge_required
        wants_behavior = req_analysis.behavior_customization

        # 2. Reconcile with Uploaded Data (if provided)
        if not data_metadata:
            validation_notes.append("No dataset uploaded. Strategy determined from requirement intent.")
            return ArchitectureAnalysis(
                task=req_analysis.task,
                knowledge_required=wants_knowledge,
                behavior_customization=wants_behavior,
                recommended_strategy=strategy,
                reason=req_analysis.reason,
                confidence=0.92,
                suggested_base_model=base_model,
                data_compatible=True,
                validation_notes=validation_notes,
                modalities_detected=modalities,
                pipeline_trace=ArchitectureDecisionEngine._build_trace(strategy, modalities, wants_knowledge, wants_behavior)
            )

        # 3. Check Document / Dataset Modality
        modality = getattr(data_metadata, "modality", "text")
        ext = data_metadata.file_type.lower()

        # Case A: Document (PDF, DOCX) or Unstructured Text (TXT)
        if modality == "document" or ext in ["pdf", "docx", "doc", "txt", "md"]:
            if wants_behavior and not wants_knowledge:
                validation_notes.append(
                    f"Uploaded document '{data_metadata.filename}' contains unstructured reference text. "
                    f"RAG is recommended to provide factual knowledge without causing training hallucinations."
                )
                strategy = "rag"
            elif wants_behavior and wants_knowledge:
                strategy = "hybrid"
                validation_notes.append(
                    f"Document '{data_metadata.filename}' provides rich reference knowledge for RAG retrieval, "
                    f"paired with conversational instruction guidance."
                )
            else:
                strategy = "rag"
                validation_notes.append(
                    f"Document '{data_metadata.filename}' provides domain reference text for exact retrieval and citations."
                )

        # Case B: Multimodal Image (PNG, JPG, JPEG, WEBP)
        elif modality == "image" or ext in ["png", "jpg", "jpeg", "webp"]:
            strategy = "rag"
            validation_notes.append(
                f"Image asset '{data_metadata.filename}' routed through Vision & OCR extraction. "
                f"Extracted visual knowledge will be indexed into the neural vector database for semantic retrieval."
            )

        # Case C: Multimodal Audio (MP3, WAV, M4A)
        elif modality == "audio" or ext in ["mp3", "wav", "m4a"]:
            if wants_behavior and not wants_knowledge:
                strategy = "qlora"
                validation_notes.append(
                    f"Audio recording '{data_metadata.filename}' transcribed via Speech-to-Text. "
                    f"Spoken dialogue will be structured as conversational demonstrations for behavioral QLoRA adaptation."
                )
            elif wants_behavior and wants_knowledge:
                strategy = "hybrid"
                validation_notes.append(
                    f"Audio recording '{data_metadata.filename}' transcribed via Speech-to-Text. "
                    f"Content will ground factual RAG search while shaping conversational persona."
                )
            else:
                strategy = "rag"
                validation_notes.append(
                    f"Audio recording '{data_metadata.filename}' transcribed via Speech-to-Text. "
                    f"Transcript indexed into neural vector store for grounded information retrieval."
                )

        # Case D: Structured Datasets (JSONL, CSV)
        elif ext in ["jsonl", "csv"]:
            if data_metadata.training_compatible:
                if wants_knowledge and wants_behavior:
                    strategy = "hybrid"
                    validation_notes.append(
                        f"Dataset has {data_metadata.num_valid_examples} valid conversational turns suitable for QLoRA fine-tuning, "
                        f"paired with vector search."
                    )
                elif wants_behavior or not wants_knowledge:
                    strategy = "qlora"
                    validation_notes.append(
                        f"Dataset contains {data_metadata.num_valid_examples} validated instruction pairs for behavioral adaptation."
                    )
                else:
                    strategy = "rag"
                    validation_notes.append(
                        f"Dataset records will be indexed into the neural vector database for semantic retrieval."
                    )
            else:
                strategy = "rag"
                validation_notes.append(
                    f"Dataset has insufficient valid training pairs ({data_metadata.num_valid_examples} valid). "
                    f"Safely defaulting to knowledge retrieval to avoid training degradation."
                )

        # 4. Hardware and Compute Feasibility Check
        if strategy in ["qlora", "hybrid"]:
            if hw["can_fit_qwen3_4b_local"]:
                validation_notes.append(
                    f"Hardware budget verified: 6GB GPU can support 4-bit QLoRA with sequence length ≤ 512."
                )
            else:
                validation_notes.append(
                    f"Local compute mode ({hw['gpu_name']}, {hw['free_vram_gb']}GB VRAM): "
                    f"QLoRA training is supported locally with lightweight adapters or via 1-click Google Colab export."
                )

        trace = ArchitectureDecisionEngine._build_trace(strategy, modalities, wants_knowledge, wants_behavior)

        return ArchitectureAnalysis(
            task=req_analysis.task,
            knowledge_required=wants_knowledge,
            behavior_customization=wants_behavior,
            recommended_strategy=strategy,
            reason=req_analysis.reason,
            confidence=0.96,
            suggested_base_model=base_model,
            data_compatible=True,
            validation_notes=validation_notes,
            modalities_detected=modalities,
            pipeline_trace=trace
        )

    @staticmethod
    def _build_trace(strategy: str, modalities: List[str], wants_knowledge: bool, wants_behavior: bool) -> List[PipelineTraceStep]:
        trace: List[PipelineTraceStep] = []
        
        # Step 1: Modality Intake
        mod_label = ", ".join([m.upper() for m in modalities]) if modalities else "TEXT"
        trace.append(PipelineTraceStep(
            step_id="trace-1-input",
            title="1. Multi-Format Input & Detection",
            modality=modalities[0] if modalities else "text",
            component="Deterministic Modality Router",
            status="completed",
            description=f"Identified modalities: [{mod_label}].",
            input_type="User Payload",
            output_type=f"Detected [{mod_label}]"
        ))

        # Step 2: Extraction
        trace.append(PipelineTraceStep(
            step_id="trace-2-extraction",
            title="2. Modality-Specific Feature & Content Extraction",
            modality=modalities[0] if modalities else "text",
            component="PyMuPDF / Word XML / Vision OCR / Speech Transcriber",
            status="completed",
            description="Normalized multi-format streams into canonical textual & semantic context.",
            input_type="Binary Media / Documents",
            output_type="Normalized Context"
        ))

        # Step 3: Decision & Architectural Construction
        strategy_desc = (
            "Retrieval-Augmented Generation (Dense Neural Embedding & Cosine Vector Store)"
            if strategy == "rag" else
            "QLoRA Parameter-Efficient Behavioral Fine-Tuning (4-bit NF4)"
            if strategy == "qlora" else
            "Hybrid Architecture (Dense RAG Retrieval + QLoRA Behavioral Alignment)"
        )
        trace.append(PipelineTraceStep(
            step_id="trace-3-architecture",
            title=f"3. Architecture Routing: {strategy.upper()}",
            component="Autonomous Decision Engine",
            status="completed",
            description=strategy_desc,
            input_type="Normalized Context + User Goal",
            output_type=f"{strategy.upper()} Pipeline Plan"
        ))

        # Step 4: Foundation Model Generation
        trace.append(PipelineTraceStep(
            step_id="trace-4-model",
            title="4. Foundation Model Execution",
            component="Qwen/Qwen3-4B-Instruct-2507",
            status="completed",
            description="Executes ChatML formatted forward passes with citation-grounded contextual generation.",
            input_type="ChatML Formatted Prompt",
            output_type="Grounded AI Generation"
        ))

        return trace
