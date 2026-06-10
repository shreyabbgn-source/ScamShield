from fastapi import APIRouter
import json, os
from collections import defaultdict

router = APIRouter()
SCAN_LOG = os.path.join(os.path.dirname(__file__), "../scan_log.jsonl")

def log_scan(result: dict, text: str):
    """Call this from your scan route after every scan."""
    entry = {
        "category": result.get("category", "unknown"),
        "risk": result.get("risk", "LOW"),
        "scam_probability": result.get("scam_probability", 0),
        "text_preview": text[:100],
    }
    with open(SCAN_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

@router.get("/api/stats")
async def get_stats():
    if not os.path.exists(SCAN_LOG):
        return {"total": 0, "categories": {}, "risk_breakdown": {}}
    
    rows = []
    with open(SCAN_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except:
                continue
    
    total = len(rows)
    categories = defaultdict(int)
    risk_breakdown = defaultdict(int)
    
    for row in rows:
        categories[row.get("category", "unknown")] += 1
        risk_breakdown[row.get("risk", "LOW")] += 1
    
    return {
        "total": total,
        "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
        "risk_breakdown": dict(risk_breakdown),
        "flagged": sum(1 for r in rows if r.get("risk") in ["HIGH", "CRITICAL"]),
        "safe": sum(1 for r in rows if r.get("risk") == "LOW"),
    }