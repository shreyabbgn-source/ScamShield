# import re
# import cv2
# import numpy as np
# from PIL import Image
# import io
# from pyzbar.pyzbar import decode as pyzbar_decode

# # ─────────────────────────────────────────────
# # KNOWN LEGITIMATE DOMAINS
# # ─────────────────────────────────────────────
# LEGIT_DOMAINS = [
#     "sbi.co.in", "icicibank.com", "hdfcbank.com", "axisbank.com",
#     "kotakbank.com", "paytm.com", "phonepe.com", "amazon.in",
#     "amazon.com", "flipkart.com", "google.com", "npci.org.in",
#     "upi.org", "bhimupi.org.in", "razorpay.com", "cashfree.com",
#     "zomato.com", "swiggy.com", "irctc.co.in", "uidai.gov.in",
#     "incometax.gov.in", "gov.in", "nic.in", "instagram.com",
#     "facebook.com", "youtube.com", "twitter.com", "linkedin.com",
# ]

# # Brand names used in impersonation
# BRAND_NAMES = [
#     "sbi", "icici", "hdfc", "axis", "kotak", "paytm", "phonepe",
#     "gpay", "googlepay", "amazon", "flipkart", "google", "microsoft",
#     "apple", "jio", "airtel", "vi", "bsnl", "irctc", "uidai",
# ]

# # Suspicious keywords in URLs
# SUSPICIOUS_URL_KEYWORDS = [
#     "kyc", "update", "verify", "secure", "login", "reward",
#     "prize", "winner", "claim", "free", "offer", "lucky",
#     "cashback", "refund", "suspend", "block", "urgent",
#     "helpdesk", "support", "help", "care", "service",
# ]

# # Suspicious UPI patterns
# SUSPICIOUS_UPI_PATTERNS = [
#     "reward", "prize", "lucky", "win", "free", "gift",
#     "kyc", "verify", "support", "help", "care",
#     "refund", "cashback", "offer",
# ]


# def decode_qr_from_image(image_bytes: bytes) -> list:
#     """
#     Decodes all QR codes found in an image.
#     Returns list of decoded strings.
#     """
#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     image_np = np.array(image)

#     decoded_objects = []

#     # Method 1: pyzbar (best for clear QR codes)
#     try:
#         results = pyzbar_decode(image_np)
#         for obj in results:
#             data = obj.data.decode("utf-8", errors="ignore").strip()
#             if data:
#                 decoded_objects.append(data)
#     except Exception:
#         pass

#     # Method 2: OpenCV QR detector (better for rotated/small QR codes)
#     if not decoded_objects:
#         try:
#             gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

#             # Try upscaling for small QR codes
#             if gray.shape[0] < 400:
#                 gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

#             detector = cv2.QRCodeDetector()
#             data, _, _ = detector.detectAndDecode(gray)
#             if data:
#                 decoded_objects.append(data)
#         except Exception:
#             pass

#     return list(set(decoded_objects))  # deduplicate


# def analyze_url(url: str) -> dict:
#     """
#     Analyzes a URL for suspicious patterns.
#     Returns risk score, flags, verdict.
#     """
#     url_lower = url.lower().strip()
#     flags = []
#     risk_score = 0

#     # Extract domain
#     domain_match = re.search(r'https?://([^/?\s]+)', url_lower)
#     domain = domain_match.group(1) if domain_match else url_lower

#     # Remove www.
#     domain = domain.replace("www.", "")

#     # Check if legitimate domain
#     is_legit = any(legit in domain for legit in LEGIT_DOMAINS)

#     # Check brand impersonation
#     impersonated_brand = None
#     for brand in BRAND_NAMES:
#         if brand in domain and not any(legit in domain for legit in LEGIT_DOMAINS):
#             impersonated_brand = brand.upper()
#             flags.append(f"Impersonates {brand.upper()}")
#             risk_score += 40
#             break

#     # Check suspicious keywords in URL
#     for kw in SUSPICIOUS_URL_KEYWORDS:
#         if kw in url_lower:
#             flags.append(f"Suspicious keyword: '{kw}'")
#             risk_score += 15
#             break

#     # Check for IP address instead of domain (very suspicious)
#     if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
#         flags.append("IP address used instead of domain")
#         risk_score += 50

#     # Check for excessive subdomains (phishing trick)
#     subdomain_count = domain.count(".")
#     if subdomain_count >= 3:
#         flags.append(f"Excessive subdomains ({subdomain_count})")
#         risk_score += 20

#     # Check for URL shorteners
#     shorteners = ["bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly",
#                   "short.ly", "rb.gy", "cutt.ly", "tiny.cc"]
#     if any(s in domain for s in shorteners):
#         flags.append("URL shortener detected — destination hidden")
#         risk_score += 35

#     # Check for typosquatting (e.g. amaz0n, g00gle)
#     typo_patterns = [
#         ("amazon", ["amaz0n", "amazom", "arnazon", "amzon"]),
#         ("google", ["g00gle", "gooogle", "googel"]),
#         ("paytm",  ["pay-tm", "paytnn", "paitm"]),
#         ("sbi",    ["sb1", "sbl"]),
#         ("icici",  ["icicl", "ic1ci"]),
#         ("hdfc",   ["hdf-c", "hdfcc"]),
#     ]
#     for real, typos in typo_patterns:
#         if any(t in domain for t in typos):
#             flags.append(f"Typosquatting of '{real}'")
#             risk_score += 45
#             break

#     # Deduct if legitimate domain
#     if is_legit:
#         risk_score = max(0, risk_score - 30)
#         flags.append("Domain matches known legitimate service")

#     # HTTP (not HTTPS) for financial URLs
#     if url_lower.startswith("http://") and any(
#         b in url_lower for b in ["bank", "pay", "upi", "kyc", "verify"]
#     ):
#         flags.append("Insecure HTTP used for financial URL")
#         risk_score += 25

#     risk_score = min(100, risk_score)

#     if risk_score >= 70:
#         verdict = "MALICIOUS"
#     elif risk_score >= 40:
#         verdict = "SUSPICIOUS"
#     else:
#         verdict = "CLEAN"

#     return {
#         "url": url,
#         "domain": domain,
#         "risk_score": risk_score,
#         "verdict": verdict,
#         "flags": flags,
#         "impersonated_brand": impersonated_brand,
#         "is_legit": is_legit,
#     }


# def analyze_upi(upi_id: str) -> dict:
#     """
#     Analyzes a UPI ID for suspicious patterns.
#     Format: name@bank or number@bank
#     """
#     upi_lower = upi_id.lower().strip()
#     flags = []
#     risk_score = 0

#     # Check for suspicious keywords in UPI ID
#     for pattern in SUSPICIOUS_UPI_PATTERNS:
#         if pattern in upi_lower:
#             flags.append(f"Suspicious keyword in UPI ID: '{pattern}'")
#             risk_score += 30

#     # Known legitimate UPI handles
#     legit_handles = [
#         "@okaxis", "@oksbi", "@okhdfcbank", "@okicici",
#         "@ybl", "@ibl", "@axl", "@paytm", "@apl",
#         "@upi", "@npci", "@sbi", "@hdfc",
#     ]
#     is_legit_handle = any(h in upi_lower for h in legit_handles)

#     # Check for random looking UPI IDs (lots of numbers)
#     numbers_in_id = len(re.findall(r'\d', upi_id))
#     if numbers_in_id > 8:
#         flags.append("Unusual number of digits in UPI ID")
#         risk_score += 15

#     if is_legit_handle and risk_score < 30:
#         verdict = "LIKELY CLEAN"
#         risk_score = max(0, risk_score - 10)
#     elif risk_score >= 50:
#         verdict = "SUSPICIOUS"
#     else:
#         verdict = "UNKNOWN"

#     return {
#         "upi_id": upi_id,
#         "risk_score": min(100, risk_score),
#         "verdict": verdict,
#         "flags": flags,
#     }


# def analyze_qr(image_bytes: bytes) -> dict:
#     """
#     Main function — decode QR, analyze content.
#     Returns full analysis dict.
#     """
#     decoded = decode_qr_from_image(image_bytes)

#     if not decoded:
#         return {
#             "qr_found": False,
#             "qr_count": 0,
#             "results": [],
#             "highest_risk": 0,
#             "summary": "No QR code detected in image.",
#         }

#     results = []
#     highest_risk = 0

#     for data in decoded:
#         data_lower = data.lower()

#         # Determine type
#         if data_lower.startswith("http") or data_lower.startswith("www"):
#             analysis = analyze_url(data)
#             analysis["type"] = "URL"
#         elif "@" in data and "upi" in data_lower or re.match(r'^[\w.]+@[\w]+$', data):
#             analysis = analyze_upi(data)
#             analysis["type"] = "UPI_ID"
#             analysis["url"] = data
#         elif data_lower.startswith("upi://"):
#             # UPI payment deep link
#             upi_match = re.search(r'pa=([\w.@]+)', data)
#             upi_id = upi_match.group(1) if upi_match else data
#             amount_match = re.search(r'am=([\d.]+)', data)
#             amount = amount_match.group(1) if amount_match else None

#             analysis = analyze_upi(upi_id)
#             analysis["type"] = "UPI_PAYMENT"
#             analysis["url"] = data
#             analysis["upi_id"] = upi_id
#             if amount:
#                 analysis["amount"] = f"₹{amount}"
#                 analysis["flags"].append(f"Payment request for ₹{amount}")
#                 analysis["risk_score"] = min(100, analysis["risk_score"] + 10)
#         else:
#             # Plain text QR
#             analysis = {
#                 "type": "TEXT",
#                 "url": data,
#                 "domain": "N/A",
#                 "risk_score": 0,
#                 "verdict": "UNKNOWN",
#                 "flags": ["Plain text QR code"],
#                 "impersonated_brand": None,
#             }

#         highest_risk = max(highest_risk, analysis.get("risk_score", 0))
#         results.append(analysis)

#     # Summary
#     if highest_risk >= 70:
#         summary = f"⚠ DANGEROUS QR code detected. {results[0].get('type', 'URL')} leads to high-risk destination."
#     elif highest_risk >= 40:
#         summary = f"⚠ Suspicious QR code. Verify before scanning or paying."
#     else:
#         summary = "QR code appears safe. Destination verified."

#     return {
#         "qr_found": True,
#         "qr_count": len(decoded),
#         "results": results,
#         "highest_risk": highest_risk,
#         "summary": summary,
#     }