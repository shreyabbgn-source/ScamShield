import re
from textblob import TextBlob
from ..models.response import ScanResponse

SCAM_PATTERNS = {
    "betting": [
        "1xbet", "parimatch", "bet now", "sports betting", "cricket betting", 
        "ipl betting", "casino", "casino bonus", "real money gaming", 
        "real cash winnings", "bet and win", "online betting",
    ],
    
    "customer_care": [
        "customer care", "helpline", "support number", "refund support", 
        "technical support", "amazon support", "flipkart support", 
        "paytm support", "phonepe support", "gpay support", "anydesk", 
        "teamviewer", "remote access",
    ],
    
    "upi": [
        "upi collect request", "scan qr", "receive money", "approve request", 
        "payment pending", "upi blocked", "upi verification", "refund pending", 
        "gpay reward", "phonepe reward", "paytm reward",
    ],

    "investment": [
        "double", "paisa double", "paise double", "double money", "double your",
        "triple your", "10x", "20x", "100x",
        "guaranteed return", "guaranteed profit", "guaranteed income", "guaranteed earning",
        "pakka munafa", "pakka kamai", "confirmed profit", "assured return",
        "25 din", "30 din", "7 din", "15 din", "60 din",
        "25 days double", "30 days double", "money in days",
        "no risk", "zero risk", "risk free", "risk-free", "bina risk",
        "100% safe", "100% profit", "200% return", "300% return",
        "high return", "high profit", "bahut jyada munafa",
        "ghar baithe", "ghar baithe kamao", "ghar se kamao",
        "घर बैठे", "घर बैठे कमाओ", "घर से कमाई",
        "daily income", "passive income", "earn daily", "rozana kamai",
        "rozana income", "har roz paisa", "daily paise",
        "invest and earn", "invest karo earn karo",
        "paisa lagao", "paise lagao", "nivesh karo", "invest now",
        "pig butchering", "fake investment app", "investment app",
        "stock market guaranteed", "share market guaranteed",
        "trading guaranteed", "forex guaranteed",
        "small investment big return", "chota invest bada return",
        "dm me for contact", "dm for details", "serious people only",
        "my friend earned", "he showed me his account",
        "mentor teaches", "the system works", "results speak",
        "started with small amount", "now earning lakhs",
        "limited people only", "only serious", "genuine people",
        "proof available", "screenshot proof", "real proof",
        "believe me it works", "tried and tested",
        "join before slots fill", "slots filling fast",
        "weekly payout", "daily payout to bank",
        "direct to bank", "direct bank transfer",
        "government approved scheme", "government backed",
        "rbi approved", "sebi approved", "pm scheme",
        "housewives can apply", "students can apply",
        "no qualification needed", "anyone can do",
        "whatsapp your name", "whatsapp name and city",
        "whatsapp to join", "message to join",
        "earn extra income", "extra income from home",
        "flexible hours earn", "free time earning",
        "online community earn", "start earning today",
        "many members earning", "register today earn",
        "learn and earn", "training provided fee",
        "small fee to join", "fee to join",
        "payment weekly whatsapp", "whatsapp for details earn",
        "2 3 hours daily earn", "students earn part time",
    ],

    "task": [
        "task complete", "task karo", "task based",
        "like and earn", "like karo paise pao", "like karo kamao",
        "rate and earn", "rating task", "rate hotels",
        "screenshot task", "screenshot bhejo", "screenshot send karo",
        "complete task earn", "per task earning", "task commission",
        "youtube like task", "instagram like task", "google review task",
        "5 star review earn", "review likhke kamao",
        "telegram task", "whatsapp task group",
        "unlock funds", "fund unlock karo", "deposit to unlock",
        "30 percent deposit", "advance deposit", "pehle paisa bhejo",
        "advance registration fee", "registration fee required",
        "security deposit required", "refundable deposit",
        "social media evaluator", "profile evaluator",
        "visit and rate", "rate profiles earn",
        "compensation after evaluation", "paid per evaluation",
        "telegram group link in bio", "whatsapp group join",
        "link in bio to join", "bio mein link hai",
    ],

    "job": [
        "part time job", "part-time job", "parttime job",
        "work from home", "work-from-home", "ghar se kaam",
        "data entry job", "online data entry",
        "earn per click", "typing job", "copy paste job",
        "online job", "freelance job guarantee",
        "10000 per month guaranteed", "20000 per month guaranteed",
        "no experience required", "freshers can apply",
        "whatsapp job", "telegram job offer",
        "join our team earn", "recruitment commission",
        "earn extra income", "extra income from home",
        "flexible hours", "part time work",
        "2 3 hours daily", "earn from phone",
    ],

    "crypto": [
        "crypto profit", "crypto guaranteed", "crypto investment",
        "bitcoin double", "bitcoin guaranteed", "btc profit",
        "ethereum guaranteed", "eth profit",
        "crypto trading guaranteed", "defi guaranteed",
        "nft profit guaranteed", "token launch earn",
        "crypto airdrop free", "free crypto",
    ],

    "lottery": [
        "you won", "aapne jeeta", "aap jeete", "congratulations you won",
        "lucky winner", "lucky draw winner", "selected winner",
        "claim your prize", "claim prize", "prize money",
        "lottery winner", "bumper prize", "iphone won",
        "car won", "gift won", "reward claim",
        "free iphone", "free laptop won",
        "spin and win", "scratch and win",
    ],

    "loan": [
        "instant loan", "instant approval", "turant loan",
        "no documents", "without documents", "bina documents",
        "guaranteed loan", "loan guarantee",
        "bad cibil loan", "no cibil check",
        "loan app download", "easy loan app",
        "1 minute loan", "5 minute loan",
    ],

    "mlm": [
        "refer and earn", "referral income", "referral commission",
        "network marketing", "mlm", "multi level",
        "chain system", "downline income", "upline income",
        "join our network", "team join karo",
        "unlimited income referral", "passive income referral",
        "binary plan", "matrix plan", "pyramid plan",
    ],

    "banking": [
        "kyc update", "kyc expire", "kyc update karne",
        "account temporarily restricted", "account restricted hai",
        "account blocked", "account suspended", "account band ho jayega",
        "otp share karo", "otp do", "otp bhejo", "otp share",
        "click karein", "link par click", "niche diye gaye link",
        "verify karne ke liye", "verify your account",
        "icici bank", "sbi bank alert", "hdfc bank alert",
        "24 ghante", "24 hours valid", "link valid",
        "temporarily restricted", "restricted hai",
        "bank account verify", "upi verify", "upi blocked",
        "aadhar link", "pan verify", "kyc pending",
        "dear customer", "bank team", "bank helpline",
        "icici-kyc", "sbi-kyc", "bank-update", "kyc-update",
        "apna kyc", "kyc karne", "kyc complete karo",
    ],

    "phishing": [
        "kyc update", "kyc expire", "kyc band ho jayega",
        "account blocked", "account suspend", "account band",
        "otp share karo", "otp do", "otp bhejo",
        "bank account verify", "upi verify", "aadhar verify",
        "click this link", "link pe click karo",
        "apk download", "app install karo",
        "sbi alert", "hdfc alert", "paytm alert", "gpay alert",
        "verify now or lose", "immediate action required",
        "your account will be closed",
    ],

    "reward": [
        "you have been selected", "you've been selected",
        "claim your", "claim now", "claim reward",
        "employee reward", "employee benefit",
        "gift card", "amazon gift card", "flipkart gift card",
        "amazon reward", "google reward", "microsoft reward",
        "you are selected", "selected as winner",
        "hard work reward", "loyalty reward",
        "redeem now", "redeem your reward",
        "limited time reward", "exclusive reward",
        "click link to claim", "visit link to claim",
        "amzn-reward", "amazn-reward", "reward.com",
        "free gift card", "win gift card",
        "congratulations selected", "lucky selected",
    ],
}

ALL_PATTERNS = [(category, phrase)
                for category, phrases in SCAM_PATTERNS.items()
                for phrase in phrases]

CATEGORY_MAP = {
    "betting":       ["1xbet", "parimatch", "bet now", "sports betting", "cricket betting", "casino"],
    "customer_care": ["customer care", "helpline", "support number", "refund support", "anydesk", "teamviewer"],
    "upi":           ["upi collect request", "scan qr", "approve request", "payment pending", "upi blocked"],
    "investment":    ["double", "guaranteed return", "no risk", "ghar baithe",
                      "daily income", "25 din", "invest", "paisa lagao",
                      "pay rs", "pay ₹", "send rs", "get back",
                      "dm me for contact", "only serious", "slots filling"],
    "crypto":        ["crypto", "bitcoin", "ethereum"],
    "lottery":       ["you won", "lucky winner", "prize", "jeeta",
                      "gift card", "claim your", "selected", "reward"],
    "job":           ["part time", "work from home", "data entry", "typing job",
                      "earn extra", "flexible hours"],
    "mlm":           ["refer and earn", "network marketing", "mlm"],
    "loan":          ["instant loan", "instant approval", "no documents"],
    "banking":       ["kyc", "kyc update", "kyc expire", "account blocked",
                      "account restricted", "otp", "upi verify",
                      "icici", "sbi", "hdfc", "temporarily restricted",
                      "24 ghante", "dear customer", "bank team"],
    "task":          ["task complete", "like karo", "screenshot bhejo",
                      "advance deposit", "registration fee", "deposit to unlock"],
    "reward":        ["gift card", "claim your", "you've been selected",
                      "employee reward", "redeem", "amazon reward"],
}

INDICATOR_MAP = {
    "customer care": "Customer-care impersonation",
    "helpline": "Support-number solicitation",
    "refund support": "Refund lure",
    
    "upi collect request": "UPI collect request",
    "approve request": "Payment approval request",
    "scan qr": "QR payment instruction",
    
    "bet now": "Betting solicitation",
    "sports betting": "Real-money betting language",
    "casino": "Online gambling language",

    "guaranteed return": "Guaranteed return promise",
    "guaranteed profit": "Guaranteed profit claim",
    "passive income": "Passive income promise",
    "daily income": "Daily earnings claim",
    "earn daily": "Daily earnings claim",
    "refer and earn": "Referral-based earnings",
    "network marketing": "MLM/network marketing language",
    "claim your prize": "Prize claim solicitation",
    "you won": "Lottery winner claim",
    "instant loan": "Instant loan offer",
    "no documents": "Loan without verification",
    "kyc update": "KYC verification request",
    "account blocked": "Account restriction threat",
    "otp": "OTP request",
    "click this link": "Suspicious link instruction",
    "work from home": "Work-from-home recruitment",
    "data entry": "Data-entry recruitment",
    "registration fee": "Upfront fee request",
    "deposit to unlock": "Unlock-payment request",
}

INDICATOR_WEIGHTS = {
    "Customer-care impersonation": 22,
    "Support-number solicitation": 20,
    "Refund lure": 22,
    
    "UPI collect request": 25,
    "Payment approval request": 25,
    "QR payment instruction": 20,
    
    "Betting solicitation": 18,
    "Real-money betting language": 20,
    "Online gambling language": 20,

    "Guaranteed return promise": 25,
    "Guaranteed profit claim": 25,
    "Passive income promise": 20,
    "Daily earnings claim": 20,
    
    "Referral-based earnings": 18,
    "MLM/network marketing language": 18,
    
    "Prize claim solicitation": 20,
    "Lottery winner claim": 25,
    
    "Instant loan offer": 15,
    "Loan without verification": 20,
    
    "KYC verification request": 20,
    "Account restriction threat": 20,
    "OTP request": 25,
    
    "Suspicious link instruction": 20,
    
    "Work-from-home recruitment": 10,
    "Data-entry recruitment": 10,
    
    "Upfront fee request": 25,
    "Unlock-payment request": 25,
    
    "Urgency language detected": 8,
    "High-confidence promotional language": 5,
}

SAFE_CONTEXT = [
    "discount", "off", "sale", "coupon", "cashback",
    "festival offer", "flat off", "upto", "up to",
    "delivery", "order", "restaurant", "food", "hotel booking",
    "movie ticket", "flight booking", "bus booking",
    "shop", "store", "brand", "product",
    "electricity bill", "recharge offer", "jio offer", "airtel offer",
]

URGENCY_WORDS = [
    "hurry", "urgent", "limited", "expires", "last chance", "only today",
    "act now", "immediately", "don't miss", "aaj hi", "abhi", "sirf aaj",
    "jaldi karo", "turant", "अभी", "जल्दी", "deadline", "closing soon",
    "seats limited", "offer ends", "last few",
]

HYPE_WORDS = [
    "guaranteed", "100%", "assured", "definitely", "absolutely",
    "no risk", "zero risk", "pakka", "bilkul safe", "100 percent",
    "pakki kamai", "confirmed profit", "always profit",
    "never loss", "loss nahi hoga",
]


def check_multiplier_scam(text: str):
    text_lower = text.lower()

    safe_contexts = [
        "off", "discount", "cashback", "sale", "coupon", "above", "over",
        "minimum", "order", "recipe", "calories", "calorie", "cal", "cals",
        "protein", "carbs", "fat", "grams", "gram", "kg", "ml", "mg",
        "nutrition", "serving", "per serving", "ingredient", "cook",
        "bake", "temperature", "degrees", "minutes", "hours", "tbsp",
        "tsp", "cup", "litre", "liter", "weight", "height", "bmi",
        "score", "rating", "review", "followers", "following", "likes",
        "views", "comments", "episode", "chapter", "page", "level",
        "floor", "km", "meter", "feet", "inch", "year", "month", "day",
        "hour", "minute", "second", "price", "rs", "₹", "percent", "%",
    ]
    for safe in safe_contexts:
        if safe in text_lower:
            return False, ""

    financial_keywords = [
        "invest", "earn", "income", "profit", "return", "paisa", "paise",
        "money", "rupee", "rupees", "kamao", "kamai", "pay", "send",
        "deposit", "withdraw", "fund", "amount",
    ]
    has_financial = any(kw in text_lower for kw in financial_keywords)
    if not has_financial:
        return False, ""

    numbers = re.findall(r'\d+', text)
    numbers = [int(n) for n in numbers if 0 < int(n) < 10_000_000]

    if len(numbers) >= 2:
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                smaller = min(numbers[i], numbers[j])
                larger = max(numbers[i], numbers[j])
                if smaller >= 50 and larger / smaller >= 4:
                    return True, f"Suspicious return: {smaller} → {larger} ({int(larger/smaller)}x)"

    return False, ""


def analyze_sentiment(text: str) -> dict:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    text_lower = text.lower()
    urgency_hits = [w for w in URGENCY_WORDS if w in text_lower]
    hype_hits = [w for w in HYPE_WORDS if w in text_lower]
    return {
        "polarity": round(polarity, 3),
        "subjectivity": round(subjectivity, 3),
        "urgency_score": round(min(1.0, len(urgency_hits) * 0.3), 3),
        "hype_score": round(min(1.0, len(hype_hits) * 0.35), 3),
        "urgency_hits": urgency_hits,
        "hype_hits": hype_hits,
    }


def sentiment_boost(sentiment: dict) -> float:
    boost = 0.0
    if sentiment["polarity"] > 0.5 and sentiment["subjectivity"] > 0.6:
        boost += 0.08
    boost += sentiment["urgency_score"] * 0.12
    boost += sentiment["hype_score"] * 0.12
    return round(min(boost, 0.22), 3)


def has_safe_context(text: str) -> bool:
    return any(word in text.lower() for word in SAFE_CONTEXT)


def detect_scam(ocr_text: str = "", caption: str = "") -> ScanResponse:
    combined = (ocr_text + " " + (caption or "")).lower()

    found_evidence = []
    category_hits = {cat: 0 for cat in SCAM_PATTERNS}

    for category, phrase in ALL_PATTERNS:
        if phrase.lower() in combined:
            indicator = INDICATOR_MAP.get(
                phrase.lower(),
                phrase.replace("_", " ").title()
            )
            if indicator not in found_evidence:
                found_evidence.append(indicator)
            category_hits[category] += 1

    is_multiplier, mult_evidence = check_multiplier_scam(combined)
    if is_multiplier:
        if mult_evidence not in found_evidence:
            found_evidence.append(mult_evidence)
        category_hits["investment"] += 2

    sentiment = analyze_sentiment(combined)
    boost = sentiment_boost(sentiment)

    if sentiment["urgency_hits"]:
        found_evidence.append("Urgency language detected")
    if sentiment["hype_hits"]:
        found_evidence.append("High-confidence promotional language")

    weighted_evidence = []
    for indicator in found_evidence:
        weighted_evidence.append({
            "indicator": indicator,
            "weight": INDICATOR_WEIGHTS.get(indicator, 5)
        })
    
    weighted_evidence.sort(key=lambda x: x["weight"], reverse=True)

    safe_penalty = 0.15 if has_safe_context(combined) and len(found_evidence) <= 2 else 0.0

    hit_count = len(found_evidence)
    if hit_count == 0:
        base = 0.04
    elif hit_count == 1:
        base = 0.55
    elif hit_count == 2:
        base = 0.73
    elif hit_count == 3:
        base = 0.86
    else:
        base = min(0.96, 0.86 + (hit_count - 3) * 0.03)

    scam_probability = max(0.02, min(0.98, base + boost - safe_penalty))
    threat_score = round(scam_probability * 100)  # ← add this line

    if scam_probability < 0.30:
        risk = "LOW"
    elif scam_probability < 0.60:
        risk = "MEDIUM"
    elif scam_probability < 0.85:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    cat_scores = {cat: 0 for cat in CATEGORY_MAP}
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in combined:
                cat_scores[cat] += 1

    best_cat = max(cat_scores, key=cat_scores.get)

    content_type = (
        best_cat.replace("_", " ").title()
        if cat_scores[best_cat] > 0
        else "General"
    )

    if cat_scores[best_cat] == 0:
        category = "Unknown"
    elif scam_probability < 0.30:
        category = "Legitimate Content"
    elif scam_probability < 0.60:
        category = "Suspicious Content"
    else:
        category = f"{content_type} Scam"

    if hit_count == 0 and boost < 0.08:
        explanation = "No cybercrime signatures detected. Content structurally appears within normal thresholds."
    else:
        parts = []
        if found_evidence:
            parts.append(
                f"Flagged {hit_count} indicator(s): "
                f"{', '.join(str(e) for e in found_evidence[:3])}"
            )
        if boost > 0.05:
            parts.append(
                f"Risk amplification via sentiment markers "
                f"(polarity {sentiment['polarity']})"
            )
        if safe_penalty > 0:
            parts.append("Risk index mitigated via standard commerce terminology rules")

        explanation = ". ".join(parts) + f". Threat Class: {category}."

    return ScanResponse(
        risk=risk,
        scam_probability=round(scam_probability, 2),
        threat_score=threat_score,
        content_type=content_type,
        category=category,
        confidence=round(scam_probability, 2),
        evidence=[str(e) for e in found_evidence[:6]],
        weighted_evidence=weighted_evidence,
        explanation=explanation,
    )