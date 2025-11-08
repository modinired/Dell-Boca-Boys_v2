import hashlib
from urllib.parse import urlparse

def canonical_id(company: str, title: str, req_id: str) -> str:
    base = f"{(company or '').strip().lower()}::{(title or '').strip().lower()}::{(req_id or '').strip().lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]

def clean_text(t: str) -> str:
    import re
    t = re.sub(r"\s+", " ", t or "").strip()
    return t

def domain(url: str) -> str:
    return urlparse(url).netloc.lower()
