from typing import Optional, List
from app.api.schemas import ArchitectureAnalysis, DatasetMetadata
from app.training.hardware_check import get_hardware_status
from app.training.model_registry import select_optimal_model

class ArchitectureDecisionEngine:
    """
    Fuses LLM requirement analysis and real data analyzer metadata with strict deterministic rules.
    Validates that the uploaded data actually supports the chosen strategy.
    """
    @staticmethod
    def resolve_architecture(
        req_analysis: ArchitectureAnalysis,
        data_metadata: Optional[DatasetMetadata] = None
    ) -> ArchitectureAnalysis:
        validation_notes: List[str] = []
        strategy = req_analysis.recommended_strategy
        hw = get_hardware_status()
        
        # Determine recommended base model from real hardware
        base_model = select_optimal_model(hw["cuda_available"], hw["free_vram_gb"])
        
        # Rule 1: If no dataset is provided
        if not data_metadata:
            validation_notes.append("No dataset uploaded. Strategy determined purely from textual requirement.")
            return ArchitectureAnalysis(
                task=req_analysis.task,
                knowledge_required=req_analysis.knowledge_required,
                behavior_customization=req_analysis.behavior_customization,
                recommended_strategy=strategy,
                reason=req_analysis.reason,
                confidence=0.90,
                suggested_base_model=base_model,
                data_compatible=True,
                validation_notes=validation_notes
            )

        # Rule 2: If PDF or TXT was uploaded, QLoRA cannot run on raw unstructured text alone
        if data_metadata.file_type in ["pdf", "txt"]:
            if strategy == "qlora":
                strategy = "rag"
                validation_notes.append(
                    f"Uploaded document '{data_metadata.filename}' is unstructured text ({data_metadata.file_type.upper()}). "
                    f"Adjusted strategy to RAG for optimal knowledge retrieval."
                )
            elif strategy == "hybrid":
                validation_notes.append(
                    f"Document '{data_metadata.filename}' provides rich domain knowledge for RAG retrieval. "
                    f"A base conversational model will be paired with the vector index."
                )

        # Rule 3: If JSONL / CSV was uploaded with chat examples
        elif data_metadata.file_type in ["jsonl", "csv"]:
            if data_metadata.training_compatible:
                if req_analysis.knowledge_required and req_analysis.behavior_customization:
                    strategy = "hybrid"
                    validation_notes.append(
                        f"Dataset has {data_metadata.num_valid_examples} valid conversational examples suitable for QLoRA training, "
                        f"paired with RAG knowledge indexing."
                    )
                elif not req_analysis.knowledge_required:
                    strategy = "qlora"
                    validation_notes.append(
                        f"Dataset contains {data_metadata.num_valid_examples} validated instruction pairs for behavioral fine-tuning."
                    )
            else:
                if strategy in ["qlora", "hybrid"]:
                    validation_notes.append(
                        f"Dataset has insufficient valid training examples ({data_metadata.num_valid_examples} valid, "
                        f"{data_metadata.num_invalid_examples} invalid). Defaulting to knowledge retrieval."
                    )
                    strategy = "rag"

        # Hardware constraints note
        if not hw["cuda_available"] and strategy in ["qlora", "hybrid"]:
            validation_notes.append(
                f"No CUDA GPU detected ({hw['device_name']}). Training will run parameter-efficient lightweight LoRA "
                f"on CPU using '{base_model}'."
            )

        return ArchitectureAnalysis(
            task=req_analysis.task,
            knowledge_required=req_analysis.knowledge_required,
            behavior_customization=req_analysis.behavior_customization,
            recommended_strategy=strategy,
            reason=req_analysis.reason,
            confidence=0.97,
            suggested_base_model=base_model,
            data_compatible=True,
            validation_notes=validation_notes
        )
