import pytesseract
from PIL import Image, ImageEnhance
import io
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

def extract_text_from_bytes(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    if image.width < 800:
        scale = 800 // image.width + 1
        image = image.resize(
            (image.width * scale, image.height * scale),
            Image.LANCZOS
        )

    image = ImageEnhance.Sharpness(image).enhance(2.0)
    image = ImageEnhance.Contrast(image).enhance(1.5)

    ocr_data = pytesseract.image_to_data(
        image, lang='eng+hin',
        output_type=pytesseract.Output.DICT
    )

    confidences = [int(c) for c in ocr_data['conf'] if str(c).isdigit() and int(c) > 0]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    text = pytesseract.image_to_string(image, lang='eng+hin').strip()

    if avg_confidence >= 70:
        visibility = "High"
    elif avg_confidence >= 45:
        visibility = "Medium"
    else:
        visibility = "Low"

    urls = re.findall(r'https?://[^\s]+|www\.[^\s]+|[a-z0-9-]+\.[a-z]{2,}\/[^\s]*', text.lower())
    suspicious_urls = []
    for url in urls:
        is_legit = any(legit in url for legit in LEGIT_DOMAINS)
        has_brand = any(brand in url for brand in BRAND_NAMES)
        if has_brand and not is_legit:
            suspicious_urls.append(url)
        elif any(kw in url for kw in ["kyc", "update", "verify", "secure", "login", "reward"]):
            suspicious_urls.append(url)

    text_lower = text.lower()
    impersonated = [b.upper() for b in BRAND_NAMES if b in text_lower]

    print(f"[OCR] Text: {text[:100]}...")
    print(f"[OCR] Confidence: {round(avg_confidence)}% | Visibility: {visibility}")

    return {
        "text": text,
        "ocr_confidence": f"{round(avg_confidence)}%",
        "text_visibility": visibility,
        "suspicious_urls": suspicious_urls,
        "brand_impersonation": impersonated,
    }