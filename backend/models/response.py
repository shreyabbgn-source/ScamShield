from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class UrlAnalysis(BaseModel):
    url: str
    domain: str
    risk_score: int
    verdict: str
    flags: List[str]
    impersonated_brand: Optional[str] = None

class ImageQuality(BaseModel):
    width: int
    height: int
    file_size_kb: float
    blur_level: str
    compression: str
    image_quality: str
    sharpness_score: float

class ScanResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Legacy & Platform Core Bindings
    risk: str  # Kept as legacy fallback mapping
    risk_level: Optional[str] = None  # Decoupled threat metric
    scam_probability: float
    threat_score: int  # Dynamic weight-based score (0-100)
    
    content_type: str = "General"
    category: str
    confidence: float
    evidence: List[str]
    explanation: str

    # OCR Telemetry Metadata
    ocr_text: Optional[str] = ""
    ocr_confidence: Optional[str] = "N/A"
    text_visibility: Optional[str] = "N/A"

    # Deep Analysis Blocks
    suspicious_urls: Optional[List[str]] = []
    brand_impersonation: Optional[List[str]] = []
    url_analysis: Optional[List[UrlAnalysis]] = []
    image_quality: Optional[ImageQuality] = None
    weighted_evidence: Optional[List[dict]] = []
    