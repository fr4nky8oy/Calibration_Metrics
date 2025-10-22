"""
ACX Audio Analyzer API - FastAPI Application
Main application file with API endpoints
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile
import os
from typing import Dict

from app.core.config import settings
from app.core.analyzer import analyze_audio_file
from app.models.schemas import (
    AnalysisResponse,
    ErrorResponse,
    HealthResponse,
    FormatsResponse
)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://calibration-metrics.vercel.app",  # Vercel deployment
        "https://analisethis.frankyredente.com",   # Custom domain
        "http://localhost:5173",                    # Local development (Vite)
        "http://localhost:3000",                    # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "ACX Audio Analyzer API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is running and ready to analyze audio files"
    )


@app.get("/api/formats", response_model=FormatsResponse)
async def get_supported_formats():
    """Get list of supported audio formats"""
    return FormatsResponse(
        supported_formats=[ext.replace(".", "").upper() for ext in settings.ALLOWED_EXTENSIONS],
        max_file_size_mb=settings.MAX_FILE_SIZE // (1024 * 1024)
    )


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze audio file for ACX and ElevenLabs compliance

    Args:
        file: Audio file to analyze (WAV, MP3, FLAC, M4A)

    Returns:
        Complete analysis results with ACX compliance, additional metrics, and ElevenLabs guidelines

    Raises:
        HTTPException: If file is invalid, too large, or analysis fails
    """

    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Create temporary file for processing
    temp_file = None
    try:
        # Read file content
        content = await file.read()

        # Check file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024 * 1024)}MB"
            )

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)

        # Analyze the audio file with original filename
        result = analyze_audio_file(temp_file_path, original_filename=file.filename)

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing audio file: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file and temp_file_path.exists():
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # Ignore cleanup errors


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            detail=str(exc.detail) if hasattr(exc, 'detail') else None
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            detail=str(exc)
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
