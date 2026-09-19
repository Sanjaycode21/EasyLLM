from typing import Optional
from app.api.schemas import ArchitectureAnalysis, DatasetMetadata
from app.architect.llm_provider import get_llm_provider

class RequirementAnalyzer:
    """
    Sends natural language requirements to configured LLMProvider
    and validates structured output against predefined schema.
    """
    @staticmethod
    async def analyze(requirement: str, dataset_metadata: Optional[DatasetMetadata] = None) -> ArchitectureAnalysis:
        provider = get_llm_provider()
        
        prompt = (
            f"You are a Principal AI Architect determining optimal model architectures.\n"
            f"User Requirement:\n\"{requirement}\"\n\n"
        )
        if dataset_metadata:
            prompt += (
                f"Uploaded Dataset Info:\n"
                f"- Filename: {dataset_metadata.filename}\n"
                f"- Type: {dataset_metadata.file_type}\n"
                f"- Records: {dataset_metadata.num_records} (Valid: {dataset_metadata.num_valid_examples}, Invalid: {dataset_metadata.num_invalid_examples})\n"
                f"- Format: {dataset_metadata.format}\n"
                f"- Training Compatible: {dataset_metadata.training_compatible}\n\n"
            )
            
        prompt += (
            "Analyze whether this system requires:\n"
            "1. 'rag': External factual knowledge lookup / documentation search without changing model behavior.\n"
            "2. 'qlora': Supervised fine-tuning / parameter-efficient adaptation to learn a specific tone, conversation style, domain syntax, or instruction behavior from training examples.\n"
            "3. 'hybrid': Both external dynamic factual grounding AND behavioral/style adaptation.\n\n"
            "Return JSON matching the schema."
        )
        
        analysis = await provider.generate_structured(prompt, ArchitectureAnalysis)
        return analysis
