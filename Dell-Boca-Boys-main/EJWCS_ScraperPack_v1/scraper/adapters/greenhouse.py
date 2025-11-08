from typing import Optional
from ..parser.jsonld_jobposting import parse_jobposting_jsonld
from ..models import JobPosting

def parse_greenhouse_job(html: str, url: str) -> Optional[JobPosting]:
    return parse_jobposting_jsonld(html, url)
