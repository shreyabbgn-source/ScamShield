import re
from textblob import TextBlob
from ..models.response import ScanResponse

SCAM_PATTERNS = {

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
    "investment": ["double", "guaranteed return", "no risk", "ghar baithe",
                   "daily income", "25 din", "invest", "paisa lagao",
                   "pay rs", "pay ₹", "send rs", "get back",
                   "dm me for contact", "only serious", "slots filling"],
    "crypto":     ["crypto", "bitcoin", "ethereum"],
    "lottery":    ["you won", "lucky winner", "prize", "jeeta",
                   "gift card", "claim your", "selected", "reward"],
    "job":        ["part time", "work from home", "data entry", "typing job",
                   "earn extra", "flexible hours"],
    "mlm":        ["refer and earn", "network marketing", "mlm"],
    "loan":       ["instant loan", "instant approval", "no documents"],
    "banking":    ["kyc", "kyc update", "kyc expire", "account blocked",
                   "account restricted", "otp", "upi verify",
                   "icici", "sbi", "hdfc", "temporarily restricted",
                   "24 ghante", "dear customer", "bank team"],
    "task":       ["task complete", "like karo", "screenshot bhejo",
                   "advance deposit", "registration fee", "deposit to unlock"],
    "reward":     ["gift card", "claim your", "you've been selected",
                   "employee reward", "redeem", "amazon reward"],
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

    # Skip if clearly food/health/fitness context
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

    # Must contain financial/investment keywords nearby
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

    numbers = re.findall(r'\d+', text)
    numbers = [int(n) for n in numbers if 0 < int(n) < 10_000_000]

    if len(numbers) >= 2:
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                smaller = min(numbers[i], numbers[j])
                larger = max(numbers[i], numbers[j])
                if smaller >= 10 and larger / smaller >= 4:
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
            found_evidence.append(phrase)
            category_hits[category] += 1

    is_multiplier, mult_evidence = check_multiplier_scam(combined)
    if is_multiplier:
        found_evidence.append(mult_evidence)
        category_hits["investment"] += 2

    sentiment = analyze_sentiment(combined)
    boost = sentiment_boost(sentiment)

    if sentiment["urgency_hits"]:
        found_evidence.append(f"Urgency: {', '.join(sentiment['urgency_hits'][:2])}")
    if sentiment["hype_hits"]:
        found_evidence.append(f"Hype language: {', '.join(sentiment['hype_hits'][:2])}")

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

    if scam_probability < 0.30:
        risk = "LOW"
    elif scam_probability < 0.60:
        risk = "MEDIUM"
    elif scam_probability < 0.85:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    # Best category using CATEGORY_MAP
    cat_scores = {cat: 0 for cat in CATEGORY_MAP}
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in combined:
                cat_scores[cat] += 1
    best_cat = max(cat_scores, key=cat_scores.get)
    category = f"{best_cat}_scam" if cat_scores[best_cat] > 0 else "unknown"

    if hit_count == 0 and boost < 0.08:
        explanation = "No scam patterns detected. Content appears safe."
    else:
        parts = []
        if found_evidence:
            parts.append(f"Found {hit_count} indicator(s): {', '.join(str(e) for e in found_evidence[:3])}")
        if boost > 0.05:
            parts.append(f"Suspicious tone (polarity {sentiment['polarity']}, subjectivity {sentiment['subjectivity']})")
        if safe_penalty > 0:
            parts.append("Partial safe context detected")
        explanation = ". ".join(parts) + f". Category: {category.replace('_', ' ')}."

    return ScanResponse(
        risk=risk,
        scam_probability=round(scam_probability, 2),
        category=category,
        confidence=round(scam_probability, 2),
        evidence=[str(e) for e in found_evidence[:6]],
        explanation=explanation,
    )