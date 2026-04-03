"""
REST API for summarization service using FastAPI
"""

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from .summarizer import TechnicalDocumentSummarizer

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Intent-Aware Document Summarizer API",
    description="Fast and multilingual document summarization service",
    version="1.0.0"
)

# Request/Response models
class SummarizeRequest(BaseModel):
    document: str
    intent: str = "technical_overview"
    language: str = "english"
    max_length: int = 150
    min_length: int = 50
    summary_level: str = "brief"  # executive, brief, detailed, bullets


class BatchSummarizeRequest(BaseModel):
    documents: List[str]
    intent: str = "technical_overview"
    language: str = "english"


class SummarizeResponse(BaseModel):
    summary: str
    intent: str
    language: str
    length: int
    quality: str


class BatchSummarizeResponse(BaseModel):
    summaries: List[str]
    count: int


# Global summarizer instance (shared for efficiency)
_summarizer = None


def get_summarizer(language: str = "english"):
    """Get or create summarizer instance (for model caching)."""
    global _summarizer
    if _summarizer is None:
        logger.info(f"Initializing summarizer with language: {language}")
        _summarizer = TechnicalDocumentSummarizer(language=language)
    return _summarizer


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    global _summarizer
    logger.info("Loading summarization model...")
    try:
        _summarizer = get_summarizer(language="english")
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Document Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "summarize": "/summarize (POST)",
            "batch": "/batch-summarize (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "ready"}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """
    Summarize a single document.
    
    Args:
        request: SummarizeRequest with document and parameters
        
    Returns:
        SummarizeResponse with summary and metrics
    """
    try:
        summarizer = get_summarizer(request.language)
        
        # Adjust parameters based on summary level
        level_params = {
            'executive': {'max_length': 50, 'min_length': 20},
            'brief': {'max_length': 100, 'min_length': 40},
            'detailed': {'max_length': 200, 'min_length': 80},
            'bullets': {'max_length': 150, 'min_length': 50}
        }
        
        params = level_params.get(request.summary_level, level_params['brief'])
        params['max_length'] = request.max_length
        params['min_length'] = request.min_length
        
        # Generate summary
        summary = summarizer.summarize(
            request.document,
            intent=request.intent,
            language=request.language,
            **params
        )
        
        # Determine quality
        quality = "high" if len(summary.split()) >= params['min_length'] else "medium"
        
        return SummarizeResponse(
            summary=summary,
            intent=request.intent,
            language=request.language,
            length=len(summary.split()),
            quality=quality
        )
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-summarize", response_model=BatchSummarizeResponse)
async def batch_summarize(request: BatchSummarizeRequest):
    """
    Summarize multiple documents (batch processing).
    
    Args:
        request: BatchSummarizeRequest with list of documents
        
    Returns:
        BatchSummarizeResponse with all summaries
    """
    try:
        summarizer = get_summarizer(request.language)
        
        summaries = []
        for doc in request.documents:
            summary = summarizer.summarize(
                doc,
                intent=request.intent,
                language=request.language
            )
            summaries.append(summary)
        
        return BatchSummarizeResponse(
            summaries=summaries,
            count=len(summaries)
        )
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages."""
    return {
        "languages": [
            "english", "spanish", "french", "german", "italian",
            "portuguese", "chinese", "japanese", "korean", "arabic",
            "hindi", "russian", "turkish", "vietnamese", "thai"
        ]
    }


@app.get("/intents")
async def get_supported_intents():
    """Get list of supported summarization intents."""
    return {
        "intents": [
            "technical_overview",
            "detailed_analysis",
            "methodology",
            "results",
            "conclusion",
            "abstract"
        ]
    }


def run_api(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the API server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    run_api()
