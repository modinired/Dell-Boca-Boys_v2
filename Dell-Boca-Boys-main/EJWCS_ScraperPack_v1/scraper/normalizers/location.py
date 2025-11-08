from typing import Optional, Dict

def normalize_location(raw: Optional[str]) -> Dict:
    if not raw:
        return {"remote": None}
    remote = any(k in raw.lower() for k in ["remote","anywhere","work from home"])
    return {"formatted": raw, "remote": remote}
