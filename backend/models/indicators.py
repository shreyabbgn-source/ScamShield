"""
Evidence indicators extracted from text
Real indicators that appear in scam messages
"""
from typing import List, Dict
from enum import Enum

class ContentType(str, Enum):
    """Content classification - what type of message is this?"""
    INVESTMENT = "Investment"
    JOB = "Job"
    LOTTERY = "Lottery"
    BETTING_GAMBLING = "Betting/Gambling"
    CRYPTO = "Crypto"
    LOAN = "Loan"
    UPI = "UPI"
    KYC = "KYC"
    REFERRAL_MLM = "Referral/MLM"
    PHISHING = "Phishing"
    FAKE_CUSTOMER_CARE = "Fake Customer Care"
    TASK = "Task"
    UNKNOWN = "Unknown"

class RiskLevel(str, Enum):
    """Risk level - severity of threat"""
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IndicatorType(str, Enum):
    """Types of indicators that signal scams"""
    URGENCY = "Urgency"
    FINANCIAL_PROMISE = "Financial Promise"
    PERSONAL_DATA_REQUEST = "Personal Data Request"
    VERIFICATION_REQUEST = "Verification Request"
    IMPERSONATION = "Brand Impersonation"
    REFERRAL_STRUCTURE = "Referral Structure"
    FAKE_AUTHORITY = "Fake Authority"
    SUSPICIOUS_LINK = "Suspicious Link"
    UNUSUAL_PAYMENT = "Unusual Payment"
    LIMITED_TIME = "Limited Time Offer"

class Indicator:
    """Single indicator found in text"""
    def __init__(self, type: IndicatorType, text: str, confidence: int = 100):
        self.type = type
        self.text = text
        self.confidence = confidence  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "text": self.text,
            "confidence": self.confidence
        }

# Indicator extraction patterns
INDICATOR_PATTERNS = {
    IndicatorType.URGENCY: [
        "urgent", "immediately", "asap", "quickly", "act now",
        "quickly", "hurry", "don't delay", "limited time",
        "abhi", "turant", "jaldi", "der mat karo"
    ],
    IndicatorType.FINANCIAL_PROMISE: [
        "double", "triple", "guaranteed profit", "guaranteed return",
        "guaranteed income", "assured earning", "passive income",
        "daily earning", "daily payout", "high return", "high profit",
        "munafa", "kamai", "returns", "earning"
    ],
    IndicatorType.PERSONAL_DATA_REQUEST: [
        "send photo", "send aadhar", "send pan", "send bank details",
        "share phone", "share email", "verify details", "confirm details",
        "provide information", "kyc process", "kyc required"
    ],
    IndicatorType.VERIFICATION_REQUEST: [
        "verify otp", "enter otp", "confirm otp", "click link",
        "update password", "verify account", "confirm account",
        "activate account", "reactivate account"
    ],
    IndicatorType.REFERRAL_STRUCTURE: [
        "referral", "refer friend", "earn from referral",
        "commission on referral", "invite friend", "recruitment",
        "mlm", "network", "downline", "upline"
    ],
    IndicatorType.FAKE_AUTHORITY: [
        "government approved", "rbi approved", "sebi approved",
        "pm scheme", "ssa approved", "official", "authorized",
        "from bank", "from government"
    ],
    IndicatorType.SUSPICIOUS_LINK: [
        "click here", "click link", "tap link", "visit link",
        "download app", "install app", "open app"
    ],
    IndicatorType.UNUSUAL_PAYMENT: [
        "western union", "google play", "itunes", "recharge",
        "bitcoin", "crypto", "gpay", "phonepay", "paytm"
    ],
    IndicatorType.LIMITED_TIME: [
        "limited slots", "limited seats", "closing soon",
        "ends today", "last day", "hurry", "slots filling",
        "fast closing"
    ]
}