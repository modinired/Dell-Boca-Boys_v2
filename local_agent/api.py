"""
Vito API - REST API for local coding agent

FastAPI-based REST interface for Vito agent
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from vito import VitoAgent, Config
from vito.config import get_config
from vito.code_tools import detect_language_from_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Vito - Local Coding Agent API",
    description="Local offline AI coding agent powered by Qwen 2.5 Coder",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Vito agent
vito: Optional[VitoAgent] = None
config = get_config()


def get_vito() -> VitoAgent:
    """Get Vito agent instance"""
    global vito
    if vito is None:
        logger.info("Initializing Vito agent...")
        vito = VitoAgent()
        logger.info("Vito agent ready")
    return vito


# Request/Response models

class ChatRequest(BaseModel):
    """Chat request"""
    message: str
    include_context: bool = True


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    timestamp: str


class CodeGenerationRequest(BaseModel):
    """Code generation request"""
    description: str
    language: str
    context: Optional[str] = None
    style: str = "modern best practices"


class CodeGenerationResponse(BaseModel):
    """Code generation response"""
    code: str
    language: str
    timestamp: str


class CodeReviewRequest(BaseModel):
    """Code review request"""
    code: str
    language: str
    focus: Optional[str] = None


class CodeReviewResponse(BaseModel):
    """Code review response"""
    review: str
    timestamp: str


class RefactorRequest(BaseModel):
    """Refactor request"""
    code: str
    language: str
    goal: str = "improve readability and maintainability"


class RefactorResponse(BaseModel):
    """Refactor response"""
    refactored_code: str
    explanation: str
    timestamp: str


class DebugRequest(BaseModel):
    """Debug request"""
    code: str
    language: str
    error: Optional[str] = None
    expected_behavior: Optional[str] = None


class DebugResponse(BaseModel):
    """Debug response"""
    analysis: str
    timestamp: str


class ExplainRequest(BaseModel):
    """Explain code request"""
    code: str
    language: str
    level: str = "detailed"


class ExplainResponse(BaseModel):
    """Explain code response"""
    explanation: str
    timestamp: str


class FileAnalysisRequest(BaseModel):
    """File analysis request"""
    file_path: str


class FileAnalysisResponse(BaseModel):
    """File analysis response"""
    analysis: Dict[str, Any]
    timestamp: str


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vito - Local Coding Agent",
        "version": "1.0.0",
        "agent": "Vito Italian (Diet Bocca)",
        "model": config.qwen_model,
        "endpoint": config.qwen_endpoint,
        "status": "ready"
    }


@app.get("/health")
async def health():
    """Health check"""
    agent = get_vito()
    stats = agent.get_stats()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_stats": stats
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with Vito

    Send a message and get a response
    """
    agent = get_vito()

    try:
        response = agent.chat(
            message=request.message,
            include_context=request.include_context,
            stream=False
        )

        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """
    Generate code from description

    Provide a description and get production-ready code
    """
    agent = get_vito()

    try:
        code = agent.generate_code(
            description=request.description,
            language=request.language,
            context=request.context,
            style=request.style
        )

        return CodeGenerationResponse(
            code=code,
            language=request.language,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """
    Review code

    Get comprehensive code review with suggestions
    """
    agent = get_vito()

    try:
        review = agent.review_code(
            code=request.code,
            language=request.language,
            focus=request.focus
        )

        return CodeReviewResponse(
            review=review,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Code review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refactor", response_model=RefactorResponse)
async def refactor_code(request: RefactorRequest):
    """
    Refactor code

    Improve code while preserving functionality
    """
    agent = get_vito()

    try:
        result = agent.refactor_code(
            code=request.code,
            language=request.language,
            goal=request.goal
        )

        # Try to extract code and explanation
        parts = result.split("```")
        if len(parts) >= 3:
            refactored = parts[1].strip()
            if refactored.startswith(request.language):
                refactored = refactored[len(request.language):].strip()
            explanation = parts[2].strip() if len(parts) > 2 else ""
        else:
            refactored = result
            explanation = ""

        return RefactorResponse(
            refactored_code=refactored,
            explanation=explanation,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Refactor error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug", response_model=DebugResponse)
async def debug_code(request: DebugRequest):
    """
    Debug code

    Find and fix bugs
    """
    agent = get_vito()

    try:
        analysis = agent.debug_code(
            code=request.code,
            language=request.language,
            error=request.error,
            expected_behavior=request.expected_behavior
        )

        return DebugResponse(
            analysis=analysis,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Debug error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain", response_model=ExplainResponse)
async def explain_code(request: ExplainRequest):
    """
    Explain code

    Get detailed explanation of what code does
    """
    agent = get_vito()

    try:
        explanation = agent.explain_code(
            code=request.code,
            language=request.language,
            level=request.level
        )

        return ExplainResponse(
            explanation=explanation,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Explain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/file", response_model=FileAnalysisResponse)
async def analyze_file(request: FileAnalysisRequest):
    """
    Analyze a code file

    Get structure analysis and metrics
    """
    agent = get_vito()

    try:
        analysis = agent.analyze_file(request.file_path)

        return FileAnalysisResponse(
            analysis=analysis,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"File analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get agent statistics"""
    agent = get_vito()
    return agent.get_stats()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat

    Send messages and receive streaming responses
    """
    await websocket.accept()
    agent = get_vito()

    try:
        while True:
            # Receive message
            message = await websocket.receive_text()

            # Stream response
            for chunk in agent.chat(message, stream=True):
                await websocket.send_text(chunk)

            # Send end marker
            await websocket.send_text("\n\n[END]")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# Startup/Shutdown events

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("="*60)
    logger.info("🎩 Vito API - Starting Up")
    logger.info("="*60)
    logger.info(f"Model: {config.qwen_model}")
    logger.info(f"Endpoint: {config.qwen_endpoint}")
    logger.info(f"Memory: {config.enable_memory}")
    logger.info("="*60)

    # Initialize agent
    get_vito()

    logger.info("✓ Vito API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🎩 Vito API - Shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level="info"
    )
