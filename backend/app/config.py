import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
MODELS_DIR = BASE_DIR / "models"
DATASETS_DIR = BASE_DIR / "datasets"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

for d in [STORAGE_DIR, MODELS_DIR, DATASETS_DIR, ARTIFACTS_DIR, VECTOR_DB_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "EasyLLM"
    version: str = "1.0.0"
    debug: bool = True
    
    # LLM Providers (OpenAI, Anthropic, Gemini, Ollama, Local)
    llm_provider: str = os.getenv("LLM_PROVIDER", "local")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    hf_token: str = os.getenv("HF_TOKEN", "")
    
    # Storage Paths
    base_dir: Path = BASE_DIR
    models_dir: Path = MODELS_DIR
    datasets_dir: Path = DATASETS_DIR
    artifacts_dir: Path = ARTIFACTS_DIR
    vector_db_dir: Path = VECTOR_DB_DIR
    
    # Default Base Model for QLoRA
    default_base_model: str = os.getenv("DEFAULT_BASE_MODEL", "Qwen/Qwen3-4B-Instruct-2507")
    
    # Embeddings model
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

settings = Settings()
