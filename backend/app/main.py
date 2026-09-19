from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router

app = FastAPI(
    title="EasyLLM API",
    description="Autonomous engine to analyze, fine-tune (QLoRA), index (RAG), evaluate and serve AI systems.",
    version="1.0.0"
)

# CORS middleware for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "EasyLLM API",
        "version": settings.version,
        "llm_provider": settings.llm_provider
    }
