"""
API routes for A/B This
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import tempfile
import os
from pathlib import Path

from ..core.config import settings
from ..core.comparator import compare_audio_files
from ..models.schemas import ComparisonResult, ErrorResponse


router = APIRouter()


@router.post("/compare", response_model=ComparisonResult)
async def compare_tracks(
    your_mix: UploadFile = File(..., description="Your mix file"),
    reference: UploadFile = File(..., description="Reference track file"),
    your_mix_start: Optional[float] = Form(None, description="Start time in seconds for your mix"),
    your_mix_end: Optional[float] = Form(None, description="End time in seconds for your mix"),
    reference_start: Optional[float] = Form(None, description="Start time in seconds for reference"),
    reference_end: Optional[float] = Form(None, description="End time in seconds for reference")
) -> Dict:
    """
    Compare your mix against a reference track

    Analyzes:
    - Frequency balance (6-band comparison)
    - Frequency masking and clarity
    - Resonances and harsh frequencies
    - Dynamic range and compression
    - LUFS loudness

    Returns comprehensive comparison with actionable EQ suggestions
    """

    # Validate file extensions
    your_mix_ext = Path(your_mix.filename).suffix.lower()
    reference_ext = Path(reference.filename).suffix.lower()

    if your_mix_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format for your mix: {your_mix_ext}. Allowed: {settings.allowed_extensions}"
        )

    if reference_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format for reference: {reference_ext}. Allowed: {settings.allowed_extensions}"
        )

    # Check file sizes
    max_size = settings.max_file_size_mb * 1024 * 1024

    # Create temporary files
    your_mix_temp = None
    reference_temp = None

    try:
        # Save uploaded files to temporary locations
        with tempfile.NamedTemporaryFile(delete=False, suffix=your_mix_ext) as your_mix_temp:
            content = await your_mix.read()

            if len(content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Your mix file too large. Max size: {settings.max_file_size_mb}MB"
                )

            your_mix_temp.write(content)
            your_mix_path = your_mix_temp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=reference_ext) as reference_temp:
            content = await reference.read()

            if len(content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Reference file too large. Max size: {settings.max_file_size_mb}MB"
                )

            reference_temp.write(content)
            reference_path = reference_temp.name

        # Perform comparison analysis
        try:
            # Create region dictionaries if provided
            your_mix_region = None
            if your_mix_start is not None and your_mix_end is not None:
                your_mix_region = {'start': your_mix_start, 'end': your_mix_end}

            reference_region = None
            if reference_start is not None and reference_end is not None:
                reference_region = {'start': reference_start, 'end': reference_end}

            results = compare_audio_files(
                your_mix_path,
                reference_path,
                downsample_sr=settings.downsample_sr,
                your_mix_region=your_mix_region,
                reference_region=reference_region
            )

            return results

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR: {error_trace}")
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )

    finally:
        # Clean up temporary files
        if your_mix_temp and os.path.exists(your_mix_path):
            os.unlink(your_mix_path)
        if reference_temp and os.path.exists(reference_path):
            os.unlink(reference_path)


@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }
