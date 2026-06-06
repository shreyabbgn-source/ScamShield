from pydantic import BaseModel
from typing import List, Optional, Any
# from pydantic import BaseModel
# from typing import List, Optional, Any

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
    risk: str
    scam_probability: float
    category: str
    confidence: float
    evidence: List[str]
    explanation: str
    ocr_text: Optional[str] = ""
    ocr_confidence: Optional[str] = "N/A"
    text_visibility: Optional[str] = "N/A"
    suspicious_urls: Optional[List[str]] = []
    brand_impersonation: Optional[List[str]] = []
    url_analysis: Optional[List[UrlAnalysis]] = []
    image_quality: Optional[ImageQuality] = None
    weighted_evidence: Optional[List[dict]] = []

# class ScanResponse(BaseModel):
#     risk: str
#     scam_probability: float
#     category: str
#     confidence: float
#     evidence: List[str]
#     explanation: str
#     ocr_text: Optional[str] = ""
#     ocr_confidence: Optional[str] = "N/A"
#     text_visibility: Optional[str] = "N/A"
#     suspicious_urls: Optional[List[str]] = []
#     brand_impersonation: Optional[List[str]] = []
#     qr_analysis: Optional[Any] = None