"""
Pydantic models and schemas for A/B This API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


# Response models

class FileInfo(BaseModel):
    """File information"""
    filename: str
    duration: float
    format: str
    sample_rate: int
    channels: int


class FrequencyBand(BaseModel):
    """Single frequency band analysis"""
    level_db: float
    energy_percent: float
    frequency_range: str


class FrequencyBalance(BaseModel):
    """Complete frequency balance analysis"""
    sub_bass: FrequencyBand
    bass: FrequencyBand
    low_mids: FrequencyBand
    mids: FrequencyBand
    high_mids: FrequencyBand
    highs: FrequencyBand


class MaskingIssue(BaseModel):
    """Frequency masking issue"""
    bands: str
    frequency_range: str
    issue: str
    severity: str
    message: str


class MaskingAnalysis(BaseModel):
    """Frequency masking results"""
    clarity_score: int = Field(..., ge=0, le=100)
    issues: List[MaskingIssue]


class Resonance(BaseModel):
    """Detected resonance"""
    frequency: float
    level: float
    prominence: float
    q_factor: float
    severity: str


class Dynamics(BaseModel):
    """Dynamic range analysis"""
    rms_db: float
    peak_db: float
    crest_factor: float
    lufs_integrated: float
    plr: float


class SpectrumData(BaseModel):
    """Spectrum visualization data"""
    frequencies: List[float]
    magnitudes: List[float]


class EQSuggestion(BaseModel):
    """EQ adjustment suggestion"""
    type: str
    frequency: int
    gain_db: float
    q: float
    message: str


class CompressionSuggestion(BaseModel):
    """Compression suggestion"""
    action: str
    amount_db: Optional[float] = None
    method: Optional[str] = None
    message: str


class TrackAnalysis(BaseModel):
    """Complete analysis for one track"""
    filename: str
    duration: float
    format: str
    sample_rate: int
    channels: int
    frequency_balance: Dict[str, Any]
    masking: MaskingAnalysis
    resonances: List[Resonance]
    dynamics: Dynamics
    spectrum_data: SpectrumData


class ComparisonResult(BaseModel):
    """Main comparison response"""
    success: bool
    processing_time: float
    your_mix: TrackAnalysis
    reference: TrackAnalysis
    comparison: Dict[str, Any]
    suggestions: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
