from datetime import timedelta
from typing import List
from pydantic import BaseModel, HttpUrl
import time

class Target(BaseModel):
    url: HttpUrl
    source: str = "ATS"
    recrawl_minutes: int = 1440

def polite_delay(base_ms: int = 800):
    time.sleep(base_ms / 1000.0)

def schedule_targets(targets: List[Target]):
    for t in targets:
        yield t
