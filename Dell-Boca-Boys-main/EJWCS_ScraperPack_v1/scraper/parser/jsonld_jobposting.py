import json
from typing import Optional
from datetime import datetime
from bs4 import BeautifulSoup
from ..models import JobPosting
from ..utils.common import canonical_id, clean_text

def _first(x):
    if isinstance(x, list): return x[0] if x else None
    return x

def parse_jobposting_jsonld(html: str, url: str) -> Optional[JobPosting]:
    soup = BeautifulSoup(html or "", "lxml")
    blocks = soup.find_all("script", {"type": "application/ld+json"})
    for tag in blocks:
        try:
            data = json.loads(tag.text)
        except Exception:
            continue
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            atype = node.get("@type") or node.get("type")
            if isinstance(atype, list):
                atype = atype[0] if atype else None
            if atype in ("JobPosting","https://schema.org/JobPosting"):
                title = clean_text(node.get("title") or node.get("name") or "")
                company = None
                h = node.get("hiringOrganization")
                if isinstance(h, dict):
                    company = clean_text(h.get("name") or "")
                loc = node.get("jobLocation") or node.get("applicantLocationRequirements")
                location_raw = None
                if isinstance(loc, list) and loc:
                    loc = loc[0]
                if isinstance(loc, dict):
                    addr = loc.get("address")
                    if isinstance(addr, dict):
                        parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
                        location_raw = ", ".join([p for p in parts if p])
                    else:
                        location_raw = clean_text(str(addr))
                desc_html = node.get("description") if isinstance(node.get("description"), str) else None
                desc_text = BeautifulSoup(desc_html or "", "lxml").get_text(" ", strip=True) if desc_html else None
                date_posted = node.get("datePosted")
                valid_through = node.get("validThrough")
                try_dt = lambda s: datetime.fromisoformat(s.replace("Z","+00:00")) if s else None
                jp = JobPosting(
                    source_url=url,
                    canonical_id=canonical_id(company or "", title, node.get("identifier") or url),
                    company_name=company,
                    title=title or "Unknown Title",
                    description_html=desc_html,
                    description_text=desc_text,
                    employment_type=_first(node.get("employmentType")) if node.get("employmentType") else None,
                    location_raw=location_raw,
                    compensation_raw=None,
                    date_posted=try_dt(date_posted),
                    valid_through=try_dt(valid_through),
                    last_seen_at=datetime.utcnow(),
                    first_seen_at=datetime.utcnow(),
                    source_type="ATS",
                )
                return jp
    return None
