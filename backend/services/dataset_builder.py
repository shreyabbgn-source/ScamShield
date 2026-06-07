import os
import re
import pandas as pd
from datasets import load_dataset

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "datasets")
SMS_PATH = os.path.join(DATA_DIR, "sms_spam", "SMSSpamCollection")


def load_sms_spam() -> list:
    """Load SMS Spam Collection dataset."""
    samples = []
    try:
        with open(SMS_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t", 1)
                if len(parts) != 2:
                    continue
                label_str, text = parts
                label = 1 if label_str.strip() == "spam" else 0
                text = text.strip()
                if len(text) > 10:
                    samples.append((text, label))
        print(f"[Dataset] SMS Spam: {len(samples)} samples")
    except Exception as e:
        print(f"[Dataset] SMS Spam load error: {e}")
    return samples


def load_huggingface_datasets() -> list:
    """Load additional datasets from HuggingFace."""
    samples = []

    # Dataset 1: Hate speech and offensive language
    # We use this to learn aggressive/manipulative language patterns
    try:
        print("[Dataset] Loading ethos dataset...")
        ds = load_dataset("ethos", "binary", trust_remote_code=True)
        for item in ds["train"]:
            text = item.get("text", "").strip()
            label = item.get("label", 0)
            if text and len(text) > 10:
                samples.append((text, label))
        print(f"[Dataset] Ethos: {len(samples)} samples added")
    except Exception as e:
        print(f"[Dataset] Ethos load error: {e}")

    # Dataset 2: Financial fraud detection
    try:
        print("[Dataset] Loading fraud detection dataset...")
        ds = load_dataset("stanfordnlp/imdb", trust_remote_code=True)
        # We don't use IMDB for scam but use it for legitimate text
        count = 0
        for item in ds["train"]:
            if count >= 500:
                break
            text = item.get("text", "").strip()[:200]
            if text and len(text) > 20:
                samples.append((text, 0))  # legitimate text
                count += 1
        print(f"[Dataset] IMDB legitimate samples: {count}")
    except Exception as e:
        print(f"[Dataset] IMDB load error: {e}")

    return samples


def load_india_scam_patterns() -> list:
    """
    Hand-curated India-specific scam patterns.
    These are based on real scams reported in India 2023-2025.
    """
    scam_samples = [
        # Investment scams
        ("Paisa double karo 25 din mein guaranteed return no risk", 1),
        ("Invest 1000 get 10000 in 30 days zero risk guaranteed profit", 1),
        ("Ghar baithe kamao daily income guaranteed 2000 rozana", 1),
        ("100% return guaranteed invest now limited slots available", 1),
        ("Rozana 5000 kamao ghar se bina kisi risk ke join now", 1),
        ("Share market guaranteed profit daily earning join telegram", 1),
        ("Crypto investment guaranteed 200% return weekly profit", 1),
        ("Trading bot guaranteed 300% return automated daily profit", 1),
        ("Invest 5000 get 50000 in one month guaranteed no loss", 1),
        ("Risk free trading earn daily guaranteed income passive", 1),
        ("Forex trading guaranteed income join now profit daily", 1),
        ("Stock tips guaranteed profit daily 1000% return weekly", 1),
        ("Binary options guaranteed profit join now earn daily", 1),
        ("Gold investment guaranteed return double money fast", 1),
        ("Real estate guaranteed income passive earning daily join", 1),
        ("Mutual fund 100% guaranteed return invest now double", 1),
        ("Small investment huge return guaranteed daily payout", 1),
        ("Earn 50000 monthly from home no experience needed join", 1),
        ("Zero risk investment double your money today guaranteed", 1),
        ("Daily profit guarantee trading signals join telegram group", 1),

        # Task scams
        ("Like karo paise pao instagram task earn 500 daily", 1),
        ("Screenshot bhejo paise milenge task complete karo now", 1),
        ("Youtube video like task 500 per task earn guaranteed", 1),
        ("Google review task earn commission 1000 daily income", 1),
        ("Rate hotels earn money telegram task group join now", 1),
        ("Complete simple tasks earn 2000 daily from home join", 1),
        ("Whatsapp task group join earn per task daily income", 1),
        ("Deposit to unlock your earned funds task withdraw now", 1),
        ("30 percent advance deposit task commission unlock funds", 1),
        ("Social media evaluator advance registration fee 299", 1),
        ("Visit profiles rate compensation evaluation telegram", 1),
        ("Amazon product rating task earn commission daily join", 1),
        ("App download task earn per download guaranteed income", 1),
        ("Survey complete earn 200 per survey daily income join", 1),
        ("Instagram like subscribe task earn commission daily", 1),

        # Job scams
        ("Work from home data entry job earn 15000 monthly guaranteed", 1),
        ("Part time job online earn 500 per hour no experience", 1),
        ("Typing job ghar baithe 20000 per month guaranteed income", 1),
        ("Copy paste job online earn daily no experience needed", 1),
        ("Freshers welcome earn 10000 weekly work from home join", 1),
        ("Whatsapp job offer earn daily from home guaranteed income", 1),
        ("Data entry work from home 25000 monthly guaranteed join", 1),
        ("Earn per click job online apply now daily income easy", 1),
        ("Telegram job offer earn 5000 daily guaranteed income", 1),
        ("Registration fee required to start earning job apply", 1),
        ("Training fee pay to learn and earn guaranteed income", 1),
        ("Advance payment required to unlock job opportunity now", 1),
        ("Earn extra income from home flexible hours whatsapp now", 1),
        ("Part time work students 2 hours daily 5000 weekly earn", 1),
        ("Work 2 hours daily earn 5000 weekly guaranteed income", 1),
        ("No qualification needed earn from phone daily income", 1),
        ("Housewife earning 30000 monthly from phone join now", 1),
        ("Simple online work daily earnings proof available dm", 1),
        ("Earn while you learn training provided small fee join", 1),
        ("Form filling job earn 300 per form daily income easy", 1),

        # Indirect scams
        ("My friend started with 5000 last month now has 87000", 1),
        ("Serious people only mentor teaches everything dm now", 1),
        ("Only genuine people dm slots filling fast limited join", 1),
        ("Government approved scheme housewives students apply now", 1),
        ("Weekly payout direct bank whatsapp name city join now", 1),
        ("Tried tested system believe me works join slots fill", 1),
        ("Proof available real screenshots dm genuine opportunity", 1),
        ("My mentor changed my life dm serious people only join", 1),
        ("I was skeptical too but now earning daily dm proof", 1),
        ("Financial freedom possible from home contact dm genuine", 1),
        ("Small investment life changing returns ask how works", 1),
        ("Quit your job work from home earn more than salary", 1),
        ("Ask me how i earn daily without leaving home genuine", 1),
        ("Limited spots available for earning program register fast", 1),
        ("Our members are earning daily results posted in group", 1),
        ("New batch starting this week only 10 slots left join", 1),
        ("Team work earn together join whatsapp group details now", 1),
        ("Passive income system once set up earns forever join", 1),
        ("Anyone can do this housewives students retired all earn", 1),
        ("Whatsapp your name city phone number to get started earn", 1),

        # Lottery scams
        ("Congratulations you won lucky draw prize claim now urgent", 1),
        ("Aapne jeeta 1 lakh rupees lucky winner selected claim", 1),
        ("Free iphone winner congratulations claim your prize now", 1),
        ("Lottery winner bumper prize claim immediately urgent now", 1),
        ("Spin and win cash prize claim now limited time only", 1),
        ("You have been selected as lucky winner claim reward now", 1),
        ("KBC winner claim your 25 lakh prize now urgent today", 1),
        ("Amazon lucky draw winner claim iphone selected now", 1),
        ("You won 500 amazon gift card claim now redeem urgent", 1),
        ("Employee reward selected claim amazon gift card now", 1),
        ("Microsoft reward program selected claim gift card now", 1),
        ("Google selected you claim free reward gift card now", 1),
        ("Loyalty reward claim amazon voucher selected now urgent", 1),
        ("Lucky customer selected free prize claim urgent now", 1),
        ("Diwali lucky draw winner claim prize now urgent today", 1),

        # Banking phishing
        ("Your sbi account will be blocked update kyc now urgent", 1),
        ("Kyc expire ho raha hai otp share karo abhi urgent", 1),
        ("Account suspend hoga turant action lo otp do now", 1),
        ("Hdfc bank alert verify account click link now urgent", 1),
        ("Paytm kyc expire click link verify immediately now", 1),
        ("Upi account blocked verify now share otp urgent now", 1),
        ("Aadhar link karo bank account band ho jayega urgent", 1),
        ("Gpay alert account suspended verify immediately now", 1),
        ("Dear customer icici bank account temporarily restricted", 1),
        ("Apna kyc update karne ke liye link par click karein", 1),
        ("Yeh link 24 ghante ke liye valid hai kyc update now", 1),
        ("Sbi alert kyc pending update immediately or blocked", 1),
        ("Axis bank account suspended kyc update urgent now", 1),
        ("Kotak bank alert verify your account immediately now", 1),
        ("Otp share karo account unlock ho jayega urgent now", 1),

        # MLM scams
        ("Refer and earn unlimited income join network now daily", 1),
        ("Network marketing join our team passive income daily", 1),
        ("MLM binary plan downline income join now earn daily", 1),
        ("Chain system refer friends earn commission unlimited", 1),
        ("Pyramid plan join early earn maximum commission now", 1),
        ("Team join karo unlimited passive income daily earn", 1),
        ("Referral income daily join our network marketing now", 1),
        ("Matrix plan join earn from downline daily income", 1),
        ("Multi level marketing guaranteed income refer earn", 1),
        ("Refer 5 people each refer 5 unlimited income chain", 1),

        # Crypto scams
        ("Bitcoin guaranteed profit invest now double weekly", 1),
        ("Ethereum double your investment crypto guaranteed return", 1),
        ("Crypto trading signals guaranteed profit daily earn", 1),
        ("Defi investment guaranteed returns passive income daily", 1),
        ("NFT flip guaranteed profit invest now limited slots", 1),
        ("Token launch early invest guaranteed 100x return now", 1),
        ("Crypto airdrop free coins claim now limited time only", 1),
        ("USDT investment guaranteed daily profit earn now join", 1),
        ("Binance trading bot guaranteed profit daily income", 1),
        ("Free bitcoin claim now limited time offer urgent", 1),

        # Loan scams
        ("Instant loan approval no documents required apply now", 1),
        ("Loan without cibil check instant disbursal today", 1),
        ("Bad credit loan guaranteed approval apply today now", 1),
        ("5 minute loan approval no verification required", 1),
        ("Guaranteed loan approval bina documents ke instant", 1),
        ("Emergency loan instant approval bad cibil ok apply", 1),
        ("Personal loan guaranteed no income proof needed now", 1),
        ("Instant 50000 loan no documents whatsapp now urgent", 1),
        ("Same day loan approval no paperwork required apply", 1),
        ("Loan app download instant money no documents needed", 1),
    ]

    # Legitimate Indian content
    legit_samples = [
        ("Recipe grilled chicken 14.7g protein 143 calories healthy", 0),
        ("Fresh homemade food delivered to your door order now", 0),
        ("50% off on orders above 300 on tuesdays food delivery", 0),
        ("Restaurant special thali only 150 rupees today lunch", 0),
        ("Biryani special offer buy one get one free today only", 0),
        ("Pizza discount 30% off on weekends order now food", 0),
        ("Healthy tiffin service 2000 per month home delivery", 0),
        ("New recipe dal makhani easy steps ingredients cook", 0),
        ("Meal prep sunday 5 meals protein carbs fat nutrition", 0),
        ("Bake chocolate cake recipe ingredients steps easy home", 0),
        ("Gym membership monthly 999 all facilities included", 0),
        ("Yoga class free trial session this week register now", 0),
        ("Workout routine 3 sets 12 reps chest shoulders day", 0),
        ("Running 5km today personal best 28 minutes fitness", 0),
        ("Diet plan 1800 calories protein 150g carbs nutrition", 0),
        ("Medicine discount 20% at apollo pharmacy this week", 0),
        ("Health checkup camp free tomorrow community center", 0),
        ("Blood donation camp register free this sunday morning", 0),
        ("Dental checkup free camp register health center visit", 0),
        ("Weight loss journey 10kg down in 3 months healthy", 0),
        ("Free online course certificate in digital marketing", 0),
        ("Engineering college admission open apply merit based", 0),
        ("UPSC preparation course join free demo class today", 0),
        ("Learn python programming online free tutorial beginner", 0),
        ("Scholarship exam results declared check marks online", 0),
        ("CBSE result declared check your marks online portal", 0),
        ("College fee payment last date reminder check portal", 0),
        ("NEET preparation tips study material free download", 0),
        ("JEE advanced result declared check rank counselling", 0),
        ("Board exam tips study schedule time management tricks", 0),
        ("Software engineer job opening apply on linkedin today", 0),
        ("Fresher job opening at infosys apply through portal", 0),
        ("Government job notification ssc cgl 2024 apply now", 0),
        ("Bank job recruitment ibps exam notification released", 0),
        ("Walk in interview tomorrow bring your resume original", 0),
        ("Internship opportunity stipend 10000 monthly learning", 0),
        ("Teacher job opening government school apply now portal", 0),
        ("TCS infosys wipro hiring freshers apply through portal", 0),
        ("Graphic designer job creative agency apply portfolio", 0),
        ("Content writer job remote apply send writing samples", 0),
        ("Amazon great indian sale starts tomorrow electronics", 0),
        ("Flipkart big billion days discount on all products", 0),
        ("Buy 2 get 1 free on all branded shirts this week", 0),
        ("Festive season discount on electronics appliances sale", 0),
        ("Sale up to 70% off on all clothing items today only", 0),
        ("New collection arrived shop now fashion clothes brand", 0),
        ("Branded shoes at factory price outlet visit today", 0),
        ("Diwali offer on home appliances discount today only", 0),
        ("End of season sale flat 40% off all items today", 0),
        ("Myntra fashion sale 50% off top brands today only", 0),
        ("Weather forecast heavy rain expected tomorrow evening", 0),
        ("Petrol diesel price today check latest rates updated", 0),
        ("New traffic rules implemented check details now", 0),
        ("Election results live updates constituency wise now", 0),
        ("IPL match today watch live score update streaming", 0),
        ("Cricket india vs australia live score update today", 0),
        ("Stock market sensex nifty today opening closing rate", 0),
        ("Budget 2024 highlights key announcements tax slabs", 0),
        ("Movie releasing this friday book tickets bookmyshow", 0),
        ("New web series releasing on netflix friday watch now", 0),
        ("Concert tickets available buy online insider today", 0),
        ("Festival celebration event free entry all welcome", 0),
        ("Comedy show tickets at flat 20% discount book now", 0),
        ("Sports tournament registration open all age groups", 0),
        ("Travel vlog himachal pradesh trip beautiful places", 0),
        ("Photography tips golden hour natural light camera", 0),
        ("Happy birthday wishes have a great year ahead today", 0),
        ("Good morning motivation quote start day positive", 0),
        ("Just love to annoy people around me funny meme", 0),
        ("Meme funny relatable daily life situations laugh", 0),
        ("Aadhaar update free service center visit apply", 0),
        ("PAN card link aadhaar last date extended check", 0),
        ("Income tax return filing deadline reminder file now", 0),
        ("Passport renewal online apply procedure easy steps", 0),
        ("Driving license renewal online portal simple steps", 0),
        ("Electricity bill pay online get cashback paytm", 0),
        ("Recharge plan new offer jio airtel vi compare now", 0),
        ("Refer a friend get 100 cashback both benefit paytm", 0),
        ("Download app get 50 rupees cashback first order", 0),
        ("Credit card reward points redeem for cashback today", 0),
        ("Cashback offer on upi payment scan and pay today", 0),
        ("First order discount 20% off use code new user", 0),
        ("Early bird discount book now save 30% travel hotel", 0),
        ("Student discount 15% off show college id valid", 0),
        ("Book fair this weekend free entry stalls available", 0),
        ("Art exhibition free entry this weekend gallery visit", 0),
        ("Pet care tips dog grooming food health vet visit", 0),
        ("Plant care monstera pothos watering sunlight tips", 0),
        ("Car review mileage performance comfort features test", 0),
        ("Phone review camera battery performance display quality", 0),
        ("DIY home decor project weekend easy steps tutorial", 0),
        ("Coffee shop review cozy ambiance good service rating", 0),
        ("Book review the alchemist paulo coelho amazing read", 0),
        ("New hairstyle loving the transformation result salon", 0),
        ("Visited mussoorie beautiful hill station trip photos", 0),
        ("Grocery shopping list weekly essentials budget plan", 0),
        ("Cooking oil price comparison brands quality review", 0),
        ("School admission form fill online documents required", 0),
        ("Library membership free books reading club join", 0),
        ("Community garden free plot allotment apply today", 0),
    ]

    print(f"[Dataset] India patterns: {len(scam_samples)} scam + {len(legit_samples)} legit")
    return scam_samples + legit_samples


def build_combined_dataset() -> tuple:
    """
    Combines all datasets into one training set.
    Returns (texts, labels).
    """
    all_samples = []

    # 1. SMS Spam dataset
    sms = load_sms_spam()
    all_samples.extend(sms)

    # 2. India-specific patterns
    india = load_india_scam_patterns()
    all_samples.extend(india)

    # 3. HuggingFace datasets
    hf = load_huggingface_datasets()
    all_samples.extend(hf)

    # Deduplicate
    seen = set()
    unique = []
    for text, label in all_samples:
        key = text.lower().strip()[:100]
        if key not in seen:
            seen.add(key)
            unique.append((text, label))

    # Stats
    scam_count = sum(1 for _, l in unique if l == 1)
    legit_count = sum(1 for _, l in unique if l == 0)
    print(f"\n[Dataset] TOTAL: {len(unique)} samples")
    print(f"[Dataset] Scam: {scam_count} | Legitimate: {legit_count}")

    texts  = [t for t, _ in unique]
    labels = [l for _, l in unique]
    return texts, labels


if __name__ == "__main__":
    texts, labels = build_combined_dataset()
    print(f"\nReady to train on {len(texts)} samples.")