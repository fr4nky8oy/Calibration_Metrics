"""
Pydantic Models for API Request/Response Schemas
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class FileInfo(BaseModel):
    """Basic file information"""
    filename: str
    duration: str  # Formatted as MM:SS or HH:MM:SS
    duration_seconds: float
    format: str
    sample_rate: int
    channels: int
    bitrate: str


class ACXCheck(BaseModel):
    """Individual ACX check result"""
    value: Any
    pass_: bool = Field(..., alias="pass")

    class Config:
        populate_by_name = True


class ACXRMSCheck(ACXCheck):
    """RMS level check"""
    range: str


class ACXPeakCheck(ACXCheck):
    """Peak level check"""
    threshold: str


class ACXNoiseFloorCheck(ACXCheck):
    """Noise floor check"""
    threshold: str


class ACXFormatCheck(ACXCheck):
    """Format check"""
    required: str


class ACXDurationCheck(ACXCheck):
    """Duration check"""
    max: int


class ACXRoomToneCheck(BaseModel):
    """Room tone check"""
    detected: bool
    pass_: bool = Field(..., alias="pass")
    required: str

    class Config:
        populate_by_name = True


class ACXCompliance(BaseModel):
    """Complete ACX compliance results"""
    overall_pass: bool
    rms: Dict[str, Any]
    peak: Dict[str, Any]
    noise_floor: Dict[str, Any]
    format: Dict[str, Any]
    duration: Dict[str, Any]
    room_tone: Dict[str, Any]


class AdditionalMetrics(BaseModel):
    """Additional audio metrics"""
    lufs: float
    true_peak: float
    reverb_level: str


class ElevenLabsCompliance(BaseModel):
    """ElevenLabs compliance results"""
    length_ok: bool
    quality_ok: bool
    length_minutes: Optional[float] = None
    length_requirement: Optional[str] = None
    quality_requirement: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    success: bool
    file_info: FileInfo
    acx_compliance: ACXCompliance
    additional_metrics: AdditionalMetrics
    elevenlabs: ElevenLabsCompliance


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str


class FormatsResponse(BaseModel):
    """Supported formats response"""
    supported_formats: list[str]
    max_file_size_mb: int
