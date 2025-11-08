from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

EmploymentType = Literal["FULL_TIME","PART_TIME","CONTRACT","INTERN","TEMPORARY","OTHER"]

class JobPosting(BaseModel):
    source_url: HttpUrl
    canonical_id: str
    company_name: Optional[str] = None
    company_canonical_id: Optional[str] = None
    title: str
    description_html: Optional[str] = None
    description_text: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    location_raw: Optional[str] = None
    location_geo: Optional[dict] = None
    compensation_raw: Optional[str] = None
    comp_annual_min: Optional[float] = None
    comp_annual_max: Optional[float] = None
    currency: Optional[str] = None
    date_posted: Optional[datetime] = None
    valid_through: Optional[datetime] = None
    seniority_tag: Optional[str] = None
    skills_raw: List[str] = []
    skills_esco: List[str] = []
    onet_occupation_id: Optional[str] = None
    responsibilities: List[str] = []
    qualifications: List[str] = []
    benefits: List[str] = []
    application_url: Optional[HttpUrl] = None
    last_seen_at: datetime
    first_seen_at: datetime
    source_type: str = "ATS"
    confidence: float = Field(ge=0, le=1, default=0.85)
