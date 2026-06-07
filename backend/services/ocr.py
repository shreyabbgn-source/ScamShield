import pytesseract
from PIL import Image, ImageEnhance
import io
import re
import cv2
import numpy as np
import easyocr

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ─────────────────────────────────────────────
# Model singletons — lazy loaded
# ─────────────────────────────────────────────
_easy_reader = None
_paddle_reader = None

def get_easy_reader():
    global _easy_reader
    if _easy_reader is None:
        print("[OCR] Loading EasyOCR...")
        _easy_reader = easyocr.Reader(['en', 'hi'])
        print("[OCR] EasyOCR ready.")
    return _easy_reader

def get_paddle_reader():
    global _paddle_reader
    if _paddle_reader is None:
        try:
            from paddleocr import PaddleOCR
            print("[OCR] Loading PaddleOCR...")
            _paddle_reader = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            print("[OCR] PaddleOCR ready.")
        except ImportError:
            print("[OCR] PaddleOCR not installed, skipping.")
            _paddle_reader = None
    return _paddle_reader

# ─────────────────────────────────────────────
# Language detection
# ─────────────────────────────────────────────
def detect_language(image_bytes: bytes) -> str:
    """
    Returns 'eng+hin' if Devanagari likely present, else 'eng'.
    Using Hindi model on pure English images hurts Tesseract accuracy.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    quick_text = pytesseract.image_to_string(pil, lang='eng').strip()
    non_ascii = sum(1 for c in quick_text if ord(c) > 127)
    ratio = non_ascii / max(len(quick_text), 1)
    return 'eng+hin' if ratio > 0.1 else 'eng'

# ─────────────────────────────────────────────
# Preprocessing — no deskew (hurts photo backgrounds)
# ─────────────────────────────────────────────
def preprocess_for_ocr(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Upscale
    scale = 2 if image.shape[1] < 800 else 1.5
    image = cv2.resize(image, None, fx=scale, fy=scale,
                       interpolation=cv2.INTER_CUBIC)

    # Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced, h=10)

    # Sharpen
    kernel = np.array([[0, -1,  0],
                       [-1,  5, -1],
                       [0, -1,  0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)

    return sharpened  # no deskew — damages photographic backgrounds

# ─────────────────────────────────────────────
# OCR engines
# ─────────────────────────────────────────────
def easyocr_extract(image_bytes: bytes) -> str:
    """EasyOCR — best for complex backgrounds and Hindi content."""
    reader = get_easy_reader()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result = reader.readtext(image, detail=1, paragraph=False)
    # Filter low confidence detections
    text = " ".join([r[1] for r in result if r[2] > 0.3])
    return text

def paddleocr_extract(image_bytes: bytes) -> str:
    """PaddleOCR — best for English on complex backgrounds."""
    reader = get_paddle_reader()
    if reader is None:
        return ""
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result = reader.ocr(image, cls=True)
    if not result or not result[0]:
        return ""
    return " ".join([line[1][0] for line in result[0] if line[1][1] > 0.5])

def tesseract_extract(image_bytes: bytes) -> tuple[str, float]:
    """Tesseract on preprocessed image — fast fallback."""
    processed = preprocess_for_ocr(image_bytes)
    pil_image = Image.fromarray(processed)
    lang = detect_language(image_bytes)
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'

    ocr_data = pytesseract.image_to_data(
        pil_image, lang=lang,
        config=custom_config,
        output_type=pytesseract.Output.DICT
    )
    confidences = [int(c) for c in ocr_data['conf']
                   if str(c).isdigit() and int(c) > 0]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    text = pytesseract.image_to_string(
        pil_image, lang=lang, config=custom_config
    ).strip()
    return text, avg_confidence

# ─────────────────────────────────────────────
# Text cleaning
# ─────────────────────────────────────────────
def clean_ocr_text(text: str) -> str:
    """Remove OCR noise and artifacts."""
    # Remove isolated single characters
    text = re.sub(r'\b[^aAiI]\b', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    # Drop lines that are pure symbols
    lines = [l for l in text.splitlines()
             if len(re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', l)) > 2]
    return ' '.join(lines).strip()

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
LEGIT_DOMAINS = [
    "sbi.co.in", "icicibank.com", "hdfcbank.com", "axisbank.com",
    "paytm.com", "phonepe.com", "amazon.in", "flipkart.com",
    "google.com", "npci.org.in", "upi.org",
]

BRAND_NAMES = [
    "sbi", "icici", "hdfc", "axis", "kotak", "paytm",
    "phonepe", "gpay", "amazon", "flipkart", "google",
    "microsoft", "apple", "jio", "airtel",
]

# ─────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────
def extract_text_from_bytes(image_bytes: bytes) -> dict:
    text = ""
    avg_confidence = 0
    method = "none"

    # ── Step 1: EasyOCR first (handles complex backgrounds + Hindi) ──
    print("[OCR] Trying EasyOCR...")
    easy_text = easyocr_extract(image_bytes)
    if len(easy_text.strip()) >= 20:
        text = easy_text
        avg_confidence = 75
        method = "EasyOCR"
        print("[OCR] EasyOCR succeeded.")

    # ── Step 2: PaddleOCR if EasyOCR weak (better for English) ──
    if len(text.strip()) < 20:
        print("[OCR] EasyOCR weak, trying PaddleOCR...")
        paddle_text = paddleocr_extract(image_bytes)
        if len(paddle_text.strip()) > len(text.strip()):
            text = paddle_text
            avg_confidence = 78
            method = "PaddleOCR"
            print("[OCR] PaddleOCR succeeded.")

    # ── Step 3: Tesseract as last resort ──
    if len(text.strip()) < 20:
        print("[OCR] Trying Tesseract fallback...")
        tess_text, avg_confidence = tesseract_extract(image_bytes)
        if len(tess_text.strip()) > len(text.strip()):
            text = tess_text
            method = "Tesseract"
            print("[OCR] Tesseract fallback used.")

    # ── Step 4: If EasyOCR succeeded but confidence borderline,
    #            try PaddleOCR and keep whichever got more text ──
    elif method == "EasyOCR" and len(text.strip()) < 60:
        paddle_text = paddleocr_extract(image_bytes)
        if len(paddle_text.strip()) > len(text.strip()) * 1.3:
            text = paddle_text
            avg_confidence = 78
            method = "PaddleOCR"

    # ── Step 5: Clean up ──
    text = clean_ocr_text(text)

    if avg_confidence >= 70:
        visibility = "High"
    elif avg_confidence >= 45:
        visibility = "Medium"
    else:
        visibility = "Low"

    # ── URL detection ──
    urls = re.findall(
        r'https?://[^\s]+|www\.[^\s]+|[a-z0-9-]+\.[a-z]{2,}\/[^\s]*',
        text.lower()
    )
    suspicious_urls = []
    for url in urls:
        is_legit = any(legit in url for legit in LEGIT_DOMAINS)
        has_brand = any(brand in url for brand in BRAND_NAMES)
        if has_brand and not is_legit:
            suspicious_urls.append(url)
        elif any(kw in url for kw in ["kyc", "update", "verify", "secure", "login", "reward"]):
            suspicious_urls.append(url)

    # ── Brand impersonation detection ──
    text_lower = text.lower()
    impersonated = [b.upper() for b in BRAND_NAMES if b in text_lower]

    word_count = len(text.split())
    print(f"[OCR] Method: {method} | Words: {word_count} | Text: {text[:100]}...")
    print(f"[OCR] Confidence: {round(avg_confidence)}% | Visibility: {visibility}")

    return {
        "text": text,
        "ocr_confidence": f"{round(avg_confidence)}%",
        "text_visibility": visibility,
        "suspicious_urls": suspicious_urls,
        "brand_impersonation": impersonated,
        "ocr_method": method,
        "word_count": word_count,
    }