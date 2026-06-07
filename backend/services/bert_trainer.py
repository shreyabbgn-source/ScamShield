import os
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from torch.utils.data import Dataset
from services.dataset_builder import build_combined_dataset

MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "bert_scam_model")


TRAINING_DATA = [
    # ── DIRECT INVESTMENT SCAMS ──
    ("paisa double karo 25 din mein guaranteed return", 1),
    ("invest 1000 get 10000 in 30 days no risk", 1),
    ("ghar baithe kamao daily income guaranteed profit", 1),
    ("100% return guaranteed invest now limited slots", 1),
    ("zero risk investment double your money today", 1),
    ("rozana 2000 kamao ghar se bina kisi risk ke", 1),
    ("share market guaranteed profit daily earning join", 1),
    ("crypto investment guaranteed 200% return weekly", 1),
    ("stock market tips guaranteed profit daily income", 1),
    ("paisa lagao rozana kamai guaranteed no loss ever", 1),
    ("small investment huge return guaranteed daily", 1),
    ("earn 50000 monthly from home no experience needed", 1),
    ("binary options guaranteed profit trading join now", 1),
    ("gold investment guaranteed return double money fast", 1),
    ("bitcoin guaranteed profit invest now double", 1),
    ("ethereum double your investment in 30 days", 1),
    ("defi guaranteed returns passive income daily earn", 1),
    ("forex trading guaranteed income join now profit", 1),
    ("mutual fund guaranteed return invest karo double", 1),
    ("real estate guaranteed income passive earning daily", 1),
    ("trading bot guaranteed 300% return automated profit", 1),
    ("invest 5000 get 50000 in one month guaranteed", 1),
    ("daily profit guarantee trading signals join now", 1),
    ("100x return crypto investment guaranteed signal", 1),
    ("risk free trading earn daily guaranteed income", 1),

    # ── TASK BASED SCAMS ──
    ("like karo paise pao instagram task earn daily", 1),
    ("screenshot bhejo paise milenge task complete karo", 1),
    ("youtube video like task 500 per task earn now", 1),
    ("google review task earn commission daily income", 1),
    ("rate hotels earn money telegram task group join", 1),
    ("complete simple tasks earn 2000 daily from home", 1),
    ("whatsapp task group join earn per task daily", 1),
    ("5 star review likhke kamao daily income guaranteed", 1),
    ("telegram task complete karo paise pao daily", 1),
    ("deposit to unlock your earned funds task now", 1),
    ("30 percent advance deposit task commission unlock", 1),
    ("task based income part time work from home earn", 1),
    ("online task complete karo 1000 per day guaranteed", 1),
    ("instagram like subscribe task earn commission daily", 1),
    ("facebook task complete earn daily income guaranteed", 1),
    ("advance registration fee 299 required task earn", 1),
    ("security deposit refundable after task completion", 1),
    ("social media evaluator visit profiles rate earn", 1),
    ("compensation after evaluation telegram group link", 1),
    ("paid per evaluation whatsapp group task income", 1),
    ("youtube rating task earn 500 per video like", 1),
    ("amazon product rating task earn commission daily", 1),
    ("app download task earn per download guaranteed", 1),
    ("survey complete earn 200 per survey daily income", 1),
    ("data collection task earn per entry daily", 1),

    # ── JOB SCAMS ──
    ("work from home data entry job earn 15000 monthly", 1),
    ("part time job online earn 500 per hour guaranteed", 1),
    ("typing job ghar baithe 20000 per month guaranteed", 1),
    ("copy paste job online earn daily no experience", 1),
    ("freshers welcome earn 10000 weekly work from home", 1),
    ("whatsapp job offer earn daily from home guaranteed", 1),
    ("online job no experience required earn now daily", 1),
    ("data entry work from home 25000 monthly guaranteed", 1),
    ("earn per click job online apply now daily income", 1),
    ("telegram job offer earn 5000 daily guaranteed", 1),
    ("recruitment commission join our team earn daily", 1),
    ("form filling job earn 300 per form daily income", 1),
    ("captcha solving job earn daily from home guaranteed", 1),
    ("registration fee required to start earning job", 1),
    ("training fee pay to learn and earn guaranteed", 1),
    ("advance payment required to unlock job opportunity", 1),
    ("earn extra income from home flexible hours whatsapp", 1),
    ("part time work students 2 hours daily 5000 weekly", 1),
    ("work 2 hours daily earn 5000 weekly guaranteed", 1),
    ("no qualification needed earn from phone daily", 1),
    ("housewife earning 30000 monthly from phone how", 1),
    ("student earning 15000 weekly from mobile join", 1),
    ("online earning no investment required daily income", 1),
    ("simple online work daily earnings proof available", 1),
    ("earn while you learn training provided fee join", 1),

    # ── INDIRECT / DISGUISED SCAMS ──
    ("my friend started with 5000 last month now has 87000", 1),
    ("serious people only mentor teaches everything results", 1),
    ("only genuine people dm slots filling fast limited", 1),
    ("government approved scheme housewives students apply", 1),
    ("weekly payout direct to bank whatsapp name city join", 1),
    ("tried and tested system believe me it works slots", 1),
    ("proof available real screenshots dm genuine opportunity", 1),
    ("friend showed account balance from investment contact", 1),
    ("my mentor changed my life dm serious people only", 1),
    ("i was skeptical too but now earning daily dm proof", 1),
    ("financial freedom possible from home contact genuine", 1),
    ("small investment life changing returns ask how works", 1),
    ("quit your job work from home earn more than salary", 1),
    ("ask me how i earn daily without leaving home genuine", 1),
    ("limited spots available for earning program register", 1),
    ("our members are earning daily results posted group", 1),
    ("new batch starting this week only 10 slots left", 1),
    ("team work earn together join whatsapp group details", 1),
    ("passive income system once set up earns forever", 1),
    ("anyone can do this housewives students retired all", 1),
    ("whatsapp your name city phone number to get started", 1),
    ("rbi approved scheme earn weekly from home apply", 1),
    ("government backed scheme direct bank transfer weekly", 1),
    ("join before slots fill limited people only serious", 1),
    ("daily payout to bank direct transfer weekly income", 1),

    # ── LOTTERY / PRIZE SCAMS ──
    ("congratulations you won lucky draw prize claim now", 1),
    ("aapne jeeta 1 lakh rupees lucky winner selected", 1),
    ("free iphone winner congratulations claim your prize", 1),
    ("lottery winner bumper prize claim immediately urgent", 1),
    ("spin and win cash prize claim now limited time only", 1),
    ("you have been selected as lucky winner claim reward", 1),
    ("scratch and win guaranteed prize redeem now urgent", 1),
    ("KBC winner claim your 25 lakh prize now urgent", 1),
    ("amazon lucky draw winner claim iphone select", 1),
    ("jio lucky draw winner claim your prize now", 1),
    ("you won 500 amazon gift card claim now redeem", 1),
    ("employee reward selected claim amazon gift card", 1),
    ("congratulations claim your 500 dollar gift card", 1),
    ("microsoft reward program selected claim gift card", 1),
    ("google selected you claim free reward gift card", 1),
    ("free gift card winner selected claim now visit link", 1),
    ("loyalty reward claim amazon voucher selected now", 1),
    ("you are winner claim gift card limited time redeem", 1),
    ("lucky customer selected free prize claim urgent", 1),
    ("diwali lucky draw winner claim prize now urgent", 1),

    # ── MLM SCAMS ──
    ("refer and earn unlimited income join network now", 1),
    ("network marketing join our team passive income daily", 1),
    ("mlm binary plan downline income join now earn", 1),
    ("chain system refer friends earn commission unlimited", 1),
    ("pyramid plan join early earn maximum commission", 1),
    ("team join karo unlimited passive income daily earn", 1),
    ("referral income daily join our network marketing", 1),
    ("matrix plan join earn from downline daily income", 1),
    ("multi level marketing guaranteed income refer earn", 1),
    ("downline commission upline income join today earn", 1),
    ("refer 5 people each refer 5 unlimited income chain", 1),
    ("join our growing team earn from every referral daily", 1),
    ("network grows you earn passive income refer join", 1),

    # ── BANKING / PHISHING SCAMS ──
    ("your sbi account will be blocked update kyc now", 1),
    ("kyc expire ho raha hai otp share karo abhi urgent", 1),
    ("account suspend hoga turant action lo otp do now", 1),
    ("hdfc bank alert verify account click link now urgent", 1),
    ("paytm kyc expire click link verify immediately now", 1),
    ("upi account blocked verify now share otp urgent", 1),
    ("aadhar link karo bank account band ho jayega urgent", 1),
    ("gpay alert account suspended verify immediately now", 1),
    ("your account will be closed click link now verify", 1),
    ("dear customer icici bank account temporarily restricted", 1),
    ("apna kyc update karne ke liye link par click karein", 1),
    ("yeh link 24 ghante ke liye valid hai kyc update", 1),
    ("bank account verify karo nahi toh band ho jayega", 1),
    ("sbi alert kyc pending update immediately or blocked", 1),
    ("axis bank account suspended kyc update urgent now", 1),
    ("kotak bank alert verify your account immediately", 1),
    ("phonepe account blocked verify kyc click link now", 1),
    ("otp share karo account unlock ho jayega urgent", 1),
    ("bank team calling verify otp on this number now", 1),
    ("icici kyc update link click verify account urgent", 1),

    # ── LOAN SCAMS ──
    ("instant loan approval no documents required apply", 1),
    ("loan without cibil check instant disbursal now", 1),
    ("bad credit loan guaranteed approval apply today", 1),
    ("5 minute loan approval no verification required", 1),
    ("loan app download instant money no documents needed", 1),
    ("guaranteed loan approval bina documents ke instant", 1),
    ("emergency loan instant approval bad cibil ok apply", 1),
    ("personal loan guaranteed no income proof needed", 1),
    ("instant 50000 loan no documents whatsapp now", 1),
    ("same day loan approval no paperwork required apply", 1),

    # ── CRYPTO SCAMS ──
    ("crypto profit guaranteed invest now double bitcoin", 1),
    ("bitcoin investment guaranteed 300% return weekly", 1),
    ("ethereum double your investment crypto guaranteed", 1),
    ("crypto trading signals guaranteed profit daily earn", 1),
    ("defi investment guaranteed returns passive income", 1),
    ("nft flip guaranteed profit invest now limited", 1),
    ("token launch early invest guaranteed 100x return", 1),
    ("crypto airdrop free coins claim now limited time", 1),
    ("usdt investment guaranteed daily profit earn now", 1),
    ("binance trading bot guaranteed profit daily income", 1),

    # ── SUBTLE SCAMS ──
    ("join our online community start earning members", 1),
    ("special scheme learn and earn small fee join", 1),
    ("limited registration open this week whatsapp join", 1),
    ("online earning community register today members", 1),
    ("we are hiring evaluators advance registration fee", 1),
    ("visit profiles rate compensation evaluation telegram", 1),
    ("social media rating job earn per rating daily", 1),
    ("app testing job earn per test daily income", 1),
    ("website visiting job earn per visit daily income", 1),
    ("ad watching job earn per ad daily income guaranteed", 1),

    # ════════════════════════════════════
    # ── LEGITIMATE CONTENT ──
    # ════════════════════════════════════

    # Food and cooking
    ("recipe grilled chicken 14.7g protein 143 calories", 0),
    ("fresh homemade food delivered to your door order", 0),
    ("50% off on orders above 300 on tuesdays food", 0),
    ("try our new menu items at discounted prices today", 0),
    ("restaurant special thali only 150 rupees today", 0),
    ("biryani special offer buy one get one free today", 0),
    ("pizza discount 30% off on weekends order now", 0),
    ("healthy tiffin service 2000 per month home delivery", 0),
    ("cake order customize your birthday cake online", 0),
    ("new recipe dal makhani easy steps ingredients cook", 0),
    ("bake chocolate cake recipe ingredients steps easy", 0),
    ("meal prep sunday 5 meals protein carbs fat grams", 0),
    ("street food tour delhi best places to eat today", 0),
    ("cooking tutorial pasta recipe 20 minutes easy", 0),
    ("nutrition facts 100g serving calories protein carbs", 0),

    # Fitness and health
    ("gym membership monthly 999 all facilities included", 0),
    ("yoga class free trial session this week register", 0),
    ("workout routine 3 sets 12 reps chest shoulders", 0),
    ("running 5km today personal best 28 minutes fitness", 0),
    ("diet plan 1800 calories protein 150g carbs 200g", 0),
    ("medicine discount 20% at apollo pharmacy this week", 0),
    ("health checkup camp free tomorrow community center", 0),
    ("blood donation camp register free this sunday", 0),
    ("dental checkup free camp register health center", 0),
    ("weight loss journey 10kg down in 3 months healthy", 0),
    ("intermittent fasting 16 8 results 2 months body", 0),
    ("protein shake recipe post workout recovery muscle", 0),
    ("bmi calculator height weight healthy range check", 0),
    ("step count 10000 steps daily health goal fitness", 0),
    ("sleep 8 hours health benefits tips better sleep", 0),

    # Education
    ("free online course certificate in digital marketing", 0),
    ("engineering college admission open apply merit", 0),
    ("upsc preparation course join free demo class", 0),
    ("learn python programming online free tutorial", 0),
    ("scholarship exam results declared check marks", 0),
    ("cbse result declared check your marks online", 0),
    ("college fee payment last date reminder portal", 0),
    ("neet preparation tips study material free download", 0),
    ("skill development course government scheme free", 0),
    ("jee advanced result declared check rank", 0),
    ("board exam tips study schedule time management", 0),
    ("online coding bootcamp learn web development", 0),
    ("mathematics tuition class grade 10 12 board", 0),
    ("english speaking course improve communication skills", 0),
    ("competitive exam books pdf free download study", 0),

    # Legitimate jobs
    ("software engineer job opening apply on linkedin", 0),
    ("fresher job opening at infosys apply through portal", 0),
    ("government job notification ssc cgl 2024 apply", 0),
    ("bank job recruitment ibps exam notification", 0),
    ("walk in interview tomorrow bring your resume", 0),
    ("internship opportunity stipend 10000 monthly learn", 0),
    ("teacher job opening government school apply now", 0),
    ("nurse recruitment government hospital vacancy", 0),
    ("police recruitment physical test schedule check", 0),
    ("tcs infosys wipro hiring freshers apply portal", 0),
    ("mba internship summer placement opportunity apply", 0),
    ("graphic designer job creative agency apply portfolio", 0),
    ("content writer job remote apply send samples", 0),
    ("sales executive job salary plus incentives apply", 0),
    ("accountant job ca inter salary 25000 apply", 0),

    # Shopping and e-commerce
    ("amazon great indian sale starts tomorrow electronics", 0),
    ("flipkart big billion days discount on products", 0),
    ("buy 2 get 1 free on all branded shirts this week", 0),
    ("festive season discount on electronics appliances", 0),
    ("sale up to 70% off on all clothing items today", 0),
    ("new collection arrived shop now fashion clothes", 0),
    ("clearance sale last few pieces remaining grab", 0),
    ("branded shoes at factory price outlet visit", 0),
    ("diwali offer on home appliances discount today", 0),
    ("end of season sale flat 40% off all items", 0),
    ("myntra fashion sale 50% off top brands today", 0),
    ("groceries at lowest price bigbasket zepto order", 0),
    ("electronics compare prices before buying tips", 0),
    ("second hand phones good condition affordable price", 0),
    ("book fair this weekend free entry stalls visit", 0),

    # News and current affairs
    ("weather forecast heavy rain expected tomorrow", 0),
    ("petrol diesel price today check latest rates", 0),
    ("new traffic rules implemented check details now", 0),
    ("election results live updates constituency wise", 0),
    ("ipl match today watch live score update", 0),
    ("cricket india vs australia live score update", 0),
    ("stock market sensex nifty today opening closing", 0),
    ("rupee dollar exchange rate today check rbi", 0),
    ("budget 2024 highlights key announcements tax", 0),
    ("new law passed parliament details read now", 0),

    # Social and entertainment
    ("movie releasing this friday book tickets bookmyshow", 0),
    ("new web series releasing on netflix friday watch", 0),
    ("concert tickets available buy online insider", 0),
    ("festival celebration event free entry all welcome", 0),
    ("comedy show tickets at flat 20% discount book", 0),
    ("sports tournament registration open all ages", 0),
    ("cultural program free entry this weekend visit", 0),
    ("art exhibition free entry weekend gallery visit", 0),
    ("just love to annoy people around me with thala", 0),
    ("happy birthday wishes have a great year ahead", 0),
    ("good morning motivation quote start day positive", 0),
    ("travel vlog himachal pradesh trip beautiful places", 0),
    ("photography tips golden hour natural light camera", 0),
    ("instagram reels trending audio follow for more", 0),
    ("meme funny relatable daily life situations laugh", 0),

    # Government and utilities
    ("aadhaar update free service center visit apply", 0),
    ("pan card link aadhaar last date extended check", 0),
    ("income tax return filing deadline reminder file", 0),
    ("passport renewal online apply procedure steps", 0),
    ("driving license renewal online portal easy", 0),
    ("voter id correction apply online free service", 0),
    ("electricity bill pay online get cashback paytm", 0),
    ("recharge plan new offer jio airtel vi compare", 0),
    ("ration card update documents required apply", 0),
    ("pm awas yojana application form fill online", 0),

    # Regular social media posts
    ("visited mussoorie beautiful hill station photos", 0),
    ("new hairstyle loving the transformation result", 0),
    ("book review the alchemist paulo coelho amazing", 0),
    ("coffee shop review cozy ambiance good service", 0),
    ("product review honest opinion pros cons", 0),
    ("diy home decor project weekend easy steps", 0),
    ("pet care tips dog grooming food health vet", 0),
    ("plant care monstera pothos watering sunlight tips", 0),
    ("car review mileage performance comfort features", 0),
    ("phone review camera battery performance display", 0),

    # Legitimate offers that could be confused
    ("refer a friend get 100 cashback both benefit paytm", 0),
    ("download app get 50 rupees cashback first order", 0),
    ("join prime membership get free delivery discount", 0),
    ("credit card reward points redeem for cashback", 0),
    ("cashback offer on upi payment scan and pay", 0),
    ("first order discount 20% off use code new user", 0),
    ("loyalty points earned on purchase redeem voucher", 0),
    ("friend referral both get discount coupon shop", 0),
    ("early bird discount book now save 30% travel", 0),
    ("student discount 15% off show college id valid", 0),
]


class ScamDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def train_bert_model():
    texts, labels = build_combined_dataset()
    print(f"[BERT] Training on {len(texts)} real samples...")

    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)
    dataset   = ScamDataset(encodings, labels)

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=2,
    )

    training_args = TrainingArguments(
        output_dir=MODEL_SAVE_PATH,
        num_train_epochs=5,
        per_device_train_batch_size=32,
        warmup_steps=50,
        weight_decay=0.01,
        logging_steps=100,
        save_strategy="no",
        report_to="none",
        learning_rate=2e-5,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    trainer.train()
    model.save_pretrained(MODEL_SAVE_PATH)
    tokenizer.save_pretrained(MODEL_SAVE_PATH)
    print("[BERT] Training complete on real dataset.")
    return model, tokenizer
