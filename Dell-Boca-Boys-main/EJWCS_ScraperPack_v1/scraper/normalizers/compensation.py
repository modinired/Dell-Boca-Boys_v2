import re
from typing import Optional, Tuple

CURRENCY = {"$":"USD","USD":"USD","GBP":"GBP","£":"GBP","EUR":"EUR","€":"EUR"}

def normalize_compensation(text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    if not text: return (None, None, None)
    t = text.replace(",", "").strip()
    cur = None
    for sym, code in CURRENCY.items():
        if sym in t or code in t.upper():
            cur = code
            break
    rng = re.findall(r"(\d+(?:\.\d+)?)", t)
    if not rng: return (None, None, cur)
    nums = list(map(float, rng))
    lo, hi = (nums[0], nums[1]) if len(nums) > 1 else (nums[0], nums[0])
    if 'k' in t.lower(): lo, hi = lo*1000, hi*1000
    if lo < 1000 and ('/hr' in t.lower() or 'hour' in t.lower()):
        lo, hi = lo*2080, hi*2080
    return (lo, hi, cur)
