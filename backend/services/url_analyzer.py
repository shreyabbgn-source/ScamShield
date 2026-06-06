import re
import socket
from datetime import datetime

KNOWN_LEGIT = [
    "sbi.co.in", "icicibank.com", "hdfcbank.com", "axisbank.com",
    "paytm.com", "phonepe.com", "amazon.in", "flipkart.com",
    "google.com", "npci.org.in", "upi.org", "ybl.co.in",
]

SUSPICIOUS_KEYWORDS = [
    "kyc", "update", "verify", "secure", "login", "reward",
    "claim", "prize", "block", "suspend", "urgent", "alert",
    "helpline", "support", "refund", "otp", "confirm",
]

TRUSTED_BRANDS = [
    "sbi", "icici", "hdfc", "axis", "kotak", "paytm",
    "phonepe", "gpay", "amazon", "flipkart", "google",
    "microsoft", "apple", "jio", "airtel", "npci", "upi",
]

def extract_urls(text: str) -> list:
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
    raw = re.findall(pattern, text)
    # Filter out noise
    cleaned = []
    for u in raw:
        u = u.strip(".,;:)")
        if len(u) > 6 and "." in u:
            cleaned.append(u.lower())
    return list(set(cleaned))

def analyze_domain(url: str) -> dict:
    # Extract domain
    domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
    domain = domain.split("/")[0].split("?")[0]

    risk_score = 0
    flags = []

    # Check if it impersonates a trusted brand
    impersonated_brand = None
    for brand in TRUSTED_BRANDS:
        if brand in domain:
            is_legit = any(domain == legit or domain.endswith("." + legit) for legit in KNOWN_LEGIT)
            if not is_legit:
                impersonated_brand = brand.upper()
                risk_score += 40
                flags.append(f"Impersonates {brand.upper()}")
            break

    # Suspicious keywords in domain
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in domain:
            risk_score += 15
            flags.append(f"Suspicious keyword: '{kw}'")
            break

    # Suspicious TLDs
    suspicious_tlds = [".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click", ".loan"]
    for tld in suspicious_tlds:
        if domain.endswith(tld):
            risk_score += 20
            flags.append(f"High-risk TLD: {tld}")
            break

    # Hyphens in domain (common in phishing like icici-kyc-update.in)
    hyphen_count = domain.count("-")
    if hyphen_count >= 2:
        risk_score += 20
        flags.append(f"Multiple hyphens in domain ({hyphen_count})")
    elif hyphen_count == 1:
        risk_score += 10
        flags.append("Hyphenated domain")

    # Long domain (phishing domains tend to be verbose)
    if len(domain) > 25:
        risk_score += 10
        flags.append("Unusually long domain")

    # Check resolvability (is it even a real domain?)
    try:
        socket.gethostbyname(domain)
        flags.append("Domain resolves (active)")
        risk_score += 5  # Active fake domains are more dangerous
    except:
        flags.append("Domain does not resolve")

    risk_score = min(99, risk_score)

    if risk_score >= 70:
        verdict = "MALICIOUS"
    elif risk_score >= 45:
        verdict = "SUSPICIOUS"
    elif risk_score >= 20:
        verdict = "UNVERIFIED"
    else:
        verdict = "SAFE"

    return {
        "url": url,
        "domain": domain,
        "risk_score": risk_score,
        "verdict": verdict,
        "flags": flags,
        "impersonated_brand": impersonated_brand,
    }

def analyze_urls_in_text(text: str) -> list:
    urls = extract_urls(text)
    results = []
    for url in urls[:5]:  # max 5 URLs
        analysis = analyze_domain(url)
        if analysis["risk_score"] > 15:  # only return non-trivial results
            results.append(analysis)
    return sorted(results, key=lambda x: x["risk_score"], reverse=True)