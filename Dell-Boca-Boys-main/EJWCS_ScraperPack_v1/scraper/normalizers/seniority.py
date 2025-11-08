def infer_seniority(title: str) -> str:
    t = (title or "").lower()
    if any(k in t for k in ["sr", "senior", "staff", "principal", "lead"]):
        return "Senior"
    if any(k in t for k in ["intern", "junior", "associate", "entry"]):
        return "Junior"
    return "Mid"
