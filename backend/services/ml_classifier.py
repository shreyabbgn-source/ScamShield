import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np

# ─────────────────────────────────────────────
# TRAINING DATA — real Indian scam patterns
# ─────────────────────────────────────────────
SCAM_SAMPLES = [
    # Investment scams
    "paisa double karo 25 din mein guaranteed return",
    "invest 1000 get 10000 in 30 days no risk",
    "ghar baithe kamao daily income guaranteed profit",
    "100% return guaranteed invest now limited slots",
    "zero risk investment double your money",
    "rozana 2000 kamao ghar se bina kisi risk ke",
    "share market guaranteed profit daily earning",
    "forex trading guaranteed income join now",
    "crypto investment guaranteed 200% return",
    "stock market tips guaranteed profit daily",
    "mutual fund guaranteed return invest karo",
    "real estate guaranteed income passive earning",
    "paisa lagao rozana kamai guaranteed no loss",
    "small investment huge return guaranteed",
    "earn 50000 monthly from home no experience",
    "binary options guaranteed profit trading",
    "gold investment guaranteed return double money",
    "bitcoin guaranteed profit invest now",
    "ethereum double your investment 30 days",
    "defi guaranteed returns passive income daily",

    # Task based scams
    "like karo paise pao instagram task earn daily",
    "screenshot bhejo paise milenge task complete karo",
    "youtube video like task 500 per task earn",
    "google review task earn commission daily",
    "rate hotels earn money telegram task group",
    "complete simple tasks earn 2000 daily from home",
    "whatsapp task group join earn per task",
    "5 star review likhke kamao daily income",
    "telegram task complete karo paise pao",
    "deposit to unlock your earned funds task",
    "30 percent advance deposit task commission unlock",
    "task based income part time work from home earn",
    "online task complete karo 1000 per day",
    "instagram like subscribe task earn commission",
    "facebook task complete earn daily income",

    # Job scams
    "work from home data entry job earn 15000 monthly",
    "part time job online earn 500 per hour",
    "typing job ghar baithe 20000 per month",
    "copy paste job online earn daily no experience",
    "freshers welcome earn 10000 weekly work from home",
    "whatsapp job offer earn daily from home",
    "online job no experience required earn now",
    "data entry work from home 25000 monthly guaranteed",
    "earn per click job online apply now",
    "telegram job offer earn 5000 daily",
    "recruitment commission join our team earn",
    "part time evening job earn extra income",
    "form filling job earn 300 per form",
    "captcha solving job earn daily from home",
    "survey job earn 200 per survey daily",

    # Lottery scams
    "congratulations you won lucky draw prize claim now",
    "aapne jeeta 1 lakh rupees lucky winner selected",
    "free iphone winner congratulations claim your prize",
    "lottery winner bumper prize claim immediately",
    "spin and win cash prize claim now limited time",
    "you have been selected as lucky winner claim reward",
    "scratch and win guaranteed prize redeem now",
    "KBC winner claim your 25 lakh prize now",
    "amazon lucky draw winner claim iphone",
    "jio lucky draw winner claim your prize",

    # MLM scams
    "refer and earn unlimited income join network",
    "network marketing join our team passive income",
    "mlm binary plan downline income join now",
    "chain system refer friends earn commission",
    "pyramid plan join early earn maximum",
    "team join karo unlimited passive income",
    "referral income daily join our network marketing",
    "matrix plan join earn from downline daily",
    "multi level marketing guaranteed income refer earn",
    "downline commission upline income join today",

    # Loan scams
    "instant loan approval no documents required",
    "loan without cibil check instant disbursal",
    "bad credit loan guaranteed approval apply now",
    "5 minute loan approval no verification",
    "loan app download instant money no documents",
    "guaranteed loan approval bina documents ke",
    "emergency loan instant approval bad cibil ok",
    "personal loan guaranteed no income proof",

    # Phishing scams
    "your sbi account will be blocked update kyc now",
    "kyc expire ho raha hai otp share karo abhi",
    "account suspend hoga turant action lo otp do",
    "hdfc bank alert verify account click link now",
    "paytm kyc expire click link verify immediately",
    "upi account blocked verify now share otp",
    "aadhar link karo bank account band ho jayega",
    "gpay alert account suspended verify immediately",
    "your account will be closed click link now",
    "bank verification required share otp urgently",

    # Hinglish mixed scams
    "bhai sirf 500 lagao aur rozana 5000 kamao guaranteed",
    "yaar paisa double hoga 15 din mein pakka",
    "ek baar invest karo zindagi bhar kamao",
    "ghar pe baithe baithe lakhon kamao daily income",
    "sach mein paisa milta hai bas task karo",
    "100 percent genuine earning opportunity join karo",
    "dosto ke saath share karo aur commission pao",
    "abhi join karo limited seats hain hurry karo",
    "sirf aaj ka offer hai kal nahi milega opportunity",
    "jaldi karo offer band hone wala hai join now",
]

LEGITIMATE_SAMPLES = [
    # Food and restaurants
    "fresh homemade food delivered to your door",
    "50% off on orders above 300 on tuesdays",
    "try our new menu items at discounted prices",
    "order now get free delivery on first order",
    "restaurant special thali only 150 rupees",
    "biryani special offer buy one get one free",
    "pizza discount 30% off on weekends",
    "healthy tiffin service 2000 per month",
    "cake order customize your birthday cake",
    "coffee shop new branch opening discount",

    # E-commerce and shopping
    "sale up to 70% off on all clothing items",
    "amazon great indian sale starts tomorrow",
    "flipkart big billion days discount offers",
    "buy 2 get 1 free on all branded shirts",
    "festive season discount on electronics",
    "new collection arrived shop now",
    "clearance sale last few pieces remaining",
    "branded shoes at factory price outlet",
    "diwali offer on home appliances discount",
    "end of season sale flat 40% off",

    # Education
    "free online course certificate in digital marketing",
    "engineering college admission open apply now",
    "upsc preparation course join free demo class",
    "learn python programming online free tutorial",
    "scholarship exam results declared check now",
    "cbse result declared check your marks",
    "college fee payment last date reminder",
    "neet preparation tips study material free",
    "skill development course government scheme",
    "free vocational training certificate course",

    # Jobs legitimate
    "software engineer job opening apply on linkedin",
    "fresher job opening at infosys apply now",
    "government job notification ssc cgl 2024",
    "bank job recruitment ibps exam notification",
    "naukri.com new job openings in your city",
    "walk in interview tomorrow bring your resume",
    "internship opportunity stipend 10000 monthly",
    "teacher job opening government school apply",
    "nurse recruitment government hospital vacancy",
    "police recruitment physical test schedule",

    # News and information
    "weather forecast rain expected tomorrow",
    "petrol diesel price today check latest rates",
    "new traffic rules implemented check details",
    "covid vaccination drive free register now",
    "aadhaar update free service center visit",
    "pan card link aadhaar last date extended",
    "income tax return filing deadline reminder",
    "passport renewal online apply procedure",
    "driving license renewal online portal",
    "voter id correction apply online free",

    # Social and entertainment
    "movie releasing this friday book tickets now",
    "ipl match today watch live on hotstar",
    "concert tickets available buy online",
    "festival celebration event free entry",
    "comedy show tickets at flat 20% discount",
    "new web series releasing on netflix friday",
    "sports tournament registration open",
    "cultural program free entry all welcome",
    "book fair this weekend entry free",
    "art exhibition free entry this weekend",

    # Health and fitness
    "gym membership monthly 999 join now",
    "yoga class free trial session this week",
    "health checkup camp free tomorrow",
    "medicine discount 20% at apollo pharmacy",
    "blood donation camp register free",
    "eye checkup free camp this sunday",
    "diet plan consultation free first session",
    "hospital opd timing changed check website",
    "dental checkup free camp register",
    "fitness app download free 30 day trial",

    # Real services
    "plumber available call for service",
    "ac repair service at home affordable",
    "car wash service at doorstep book now",
    "cab service book at lowest fare",
    "electricity bill pay online get cashback",
    "recharge plan new offer jio airtel vi",
    "house painting service free estimate",
    "pest control service affordable rates",
    "internet connection new plan launched",
    "courier service same day delivery available",

    # Indirect / disguised scams
    "my friend started with 5000 last month now has 87000 dm me for contact",
    "serious people only mentor teaches everything results speak for themselves",
    "started with small amount now earning daily proof available screenshot",
    "only genuine people dm me slots filling fast limited people joining",
    "we are hiring social media evaluators advance registration fee 299 required",
    "visit profiles rate them compensation after evaluation telegram group link bio",
    "government approved scheme housewives students can apply no qualification needed",
    "weekly payout direct to bank whatsapp your name and city to join",
    "limited registration open this week only whatsapp to join earn weekly",
    "tried and tested system believe me it works join before slots fill",
    "my mentor changed my life dm for details only serious people contact",
    "refundable security deposit required after task completion funds released",
    "social media evaluation job work from home compensation per profile rated",
    "government backed scheme direct bank transfer weekly no experience needed",
    "proof available real screenshots dm me genuine opportunity limited slots",
    "friend showed account balance 87000 from 5000 investment want his contact",
    "registration fee refundable after first payout join telegram group now",
    "anyone can do this housewives students retired people all earning daily",
    "whatsapp name city phone number to get started weekly bank payout",
    "rbi approved scheme earn weekly from home no qualification apply now",

    "you have been selected claim your amazon gift card employee reward",
    "congratulations claim your 500 dollar gift card redeem now link",
    "employee reward selected claim amazon gift card hard work",
    "free gift card winner selected claim now visit link redeem",
    "microsoft reward program selected claim your gift card now",
    "google selected you claim free reward gift card click link",
    "loyalty reward claim your amazon voucher selected employee",
    "you are winner claim gift card limited time redeem now",
    
    # Phishing / bank fraud patterns (from MHA brochure)
"may i have your account details otp password",
"share your otp atm pin cvv urgent bank verification",
"your account will be blocked share otp immediately",
"net banking password required urgent verification",
"bank employee calling for account details otp",

# Too good to be true (tip #25 explicitly)
"earn money with little or no work guaranteed",
"make money on investment with little or no risk",
"too good to be true earn from home no work",

# Fake emergency scam (tip #23)
"your family member met accident urgent money transfer needed",
"hospital calling emergency money required transfer now",
"accident hospital urgent fund transfer family member",

# Fake app/link scams (tip #26, #28)  
"click link install ewallet app sms social media",
"download app link whatsapp earn money install now",
# ── From MHA Cybercrime Brochure — Scam patterns ──
# Bank/OTP phishing
"may i have your account details sir bank employee calling",
"share your otp atm pin cvv number bank verification urgent",
"net banking password required share immediately account blocked",
"bank calling verify account details otp password urgent",
"email from bank click link verify account details now",
"your bank account will be suspended share otp immediately",
"cvv number expiry date required bank verification call",
"phone banking pin required urgent bank employee calling",
"bank alert account suspended verify otp click link now",
"netbanking password share karo account band ho jayega",

# Too good to be true investment
"earn money with little or no work guaranteed daily income",
"make money on investment with little or no risk guaranteed",
"too good to be true offer earn from home no experience",
"small investment huge returns guaranteed no risk involved",
"earn daily income from home with zero effort guaranteed",

# Fake emergency scam
"your family member met accident urgent money transfer needed",
"hospital calling emergency money required transfer now",
"accident hospital urgent fund transfer family member injured",
"your son met accident send money urgently hospital calling",
"emergency transfer money family member accident hospital",

# Fake app and link scams
"click link install ewallet app sms whatsapp social media",
"download app link whatsapp earn money install now",
"install app link shared sms get reward cashback now",
"follow link download banking app verify account click",
"app link shared email install immediately account verify",

# Fake shopping/deal scams
"search engine result best deal click shop now lowest price",
"unknown website huge discount buy now limited time offer",
"50% off all products shop now unfamiliar website deal",
"buy now huge discount unknown site click link shop",

# Card cloning / ATM fraud
"card details required swipe pos terminal sales person",
"atm pin capture cctv keylogger public computer banking",
"save card details ewallet secure convenient shop online",
"public wifi banking transaction safe secure login now",
"autofill card number cvv browser form online payment",

# Impersonation scams
"posing as bank employee requesting otp account details",
"claiming to be from bank asking password pin cvv urgent",
"fake bank email link verify account details click now",
"third party extension plugin browser track activity steal",
"keylogger public computer capture password bank details",
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "scam_model.pkl")


def train_model():
    from services.dataset_builder import build_combined_dataset
    texts, labels = build_combined_dataset()
    print(f"[ML] Training TF-IDF on {len(texts)} samples...")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=10000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", LogisticRegression(
            C=1.5,
            max_iter=1000,
            class_weight="balanced",
        )),
    ])

    pipeline.fit(texts, labels)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    print(f"[ML] Model trained on {len(texts)} samples and saved.")
    return pipeline


def ml_scam_score(text: str) -> float:
    """Returns probability 0.0-1.0 that text is a scam."""
    if _model is None:
        raise RuntimeError("[ML] Model not loaded.")
    if not text.strip():
        return 0.5
    proba = _model.predict_proba([text.lower()])[0]
    return round(float(proba[1]), 3)

# Add this function after train_model()
def load_model():
    global _model
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        print("[ML] Model loaded from disk.")
    else:
        print("[ML] No saved model found, training new model...")
        _model = train_model()

# ── Module-level init (runs on import) ──
_model = None
load_model()