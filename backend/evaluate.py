"""
Run this after training to get accuracy metrics.
Command: python evaluate.py
"""
from .services.bert_classifier import bert_scam_score
from .services.ml_classifier import ml_scam_score
from .services.ensemble import ensemble_detect

# 30 test cases with known labels
# 1 = scam, 0 = legitimate
TEST_CASES = [
    # SCAM cases
    ("Paisa double karo 25 din mein guaranteed return no risk", 1),
    ("Your SBI account blocked update KYC now click link urgent", 1),
    ("Congratulations you won lucky draw prize claim now urgent", 1),
    ("Like karo paise pao instagram task earn 500 daily", 1),
    ("Work from home data entry job earn 15000 monthly guaranteed", 1),
    ("Bitcoin guaranteed profit invest now double weekly return", 1),
    ("Refer and earn unlimited income join network marketing now", 1),
    ("Instant loan approval no documents required bad cibil ok", 1),
    ("My friend started 5000 now has 87000 dm me serious only", 1),
    ("Government approved scheme housewives apply weekly payout", 1),
    ("Free iphone winner congratulations claim prize now urgent", 1),
    ("Deposit to unlock your earned funds task advance required", 1),
    ("Kyc expire otp share karo account band ho jayega urgent", 1),
    ("Earn 50000 monthly from home no experience needed join now", 1),
    ("Crypto trading signals guaranteed profit daily earn join", 1),

    # LEGITIMATE cases
    ("Recipe grilled chicken 14.7g protein 143 calories healthy", 0),
    ("Fresh homemade food delivered to your door 50% off today", 0),
    ("Software engineer job opening apply on linkedin today", 0),
    ("IPL match today watch live score update streaming now", 0),
    ("CBSE result declared check your marks online portal", 0),
    ("Amazon great indian sale starts tomorrow electronics", 0),
    ("Gym membership monthly 999 all facilities included join", 0),
    ("Just love to annoy people around me funny meme thala", 0),
    ("Weather forecast heavy rain expected tomorrow evening", 0),
    ("Happy birthday wishes have a great year ahead today", 0),
    ("Refer a friend get 100 cashback both benefit paytm app", 0),
    ("50% off on orders above 300 tuesdays food delivery", 0),
    ("UPSC preparation course join free demo class today", 0),
    ("Blood donation camp register free this sunday morning", 0),
    ("New web series releasing on netflix friday watch now", 0),
]


def evaluate():
    print("=" * 55)
    print("ScamShield AI — Model Evaluation Report")
    print("=" * 55)

    results = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    bert_results = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}

    for text, true_label in TEST_CASES:
        # Ensemble prediction
        result = ensemble_detect(caption=text)
        pred = 1 if result.scam_probability >= 0.5 else 0

        if true_label == 1 and pred == 1:
            results["tp"] += 1
        elif true_label == 0 and pred == 0:
            results["tn"] += 1
        elif true_label == 0 and pred == 1:
            results["fp"] += 1
            print(f"  ❌ FALSE POSITIVE: {text[:60]}...")
        elif true_label == 1 and pred == 0:
            results["fn"] += 1
            print(f"  ❌ FALSE NEGATIVE: {text[:60]}...")

        # BERT only
        bert_score = bert_scam_score(text)
        bert_pred = 1 if bert_score >= 0.5 else 0
        if true_label == 1 and bert_pred == 1:
            bert_results["tp"] += 1
        elif true_label == 0 and bert_pred == 0:
            bert_results["tn"] += 1
        elif true_label == 0 and bert_pred == 1:
            bert_results["fp"] += 1
        elif true_label == 1 and bert_pred == 0:
            bert_results["fn"] += 1

    def metrics(r, name):
        total = sum(r.values())
        accuracy  = (r["tp"] + r["tn"]) / total * 100
        precision = r["tp"] / (r["tp"] + r["fp"]) * 100 if (r["tp"] + r["fp"]) > 0 else 0
        recall    = r["tp"] / (r["tp"] + r["fn"]) * 100 if (r["tp"] + r["fn"]) > 0 else 0
        fpr       = r["fp"] / (r["fp"] + r["tn"]) * 100 if (r["fp"] + r["tn"]) > 0 else 0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        print(f"\n{name}")
        print(f"  Accuracy:           {accuracy:.1f}%")
        print(f"  Precision:          {precision:.1f}%")
        print(f"  Recall:             {recall:.1f}%")
        print(f"  F1 Score:           {f1:.1f}%")
        print(f"  False Positive Rate:{fpr:.1f}%")
        print(f"  TP:{r['tp']} TN:{r['tn']} FP:{r['fp']} FN:{r['fn']}")

    metrics(results, "4-Layer Ensemble")
    metrics(bert_results, "BERT Only")

    print("\n" + "=" * 55)
    print(f"Test samples: {len(TEST_CASES)} ({sum(1 for _,l in TEST_CASES if l==1)} scam, {sum(1 for _,l in TEST_CASES if l==0)} legit)")
    print("=" * 55)


if __name__ == "__main__":
    evaluate()