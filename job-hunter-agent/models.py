from typing import List
from pydantic import BaseModel, field_validator
from datetime import date


class Job(BaseModel):

    job_title: str
    company_name: str
    job_location: str
    is_remote_friendly: bool | None = None
    employment_type: str | None = None
    compensation: str | None = None
    job_posting_url: str
    job_summary: str

    key_qualifications: List[str] | None = None
    job_responsibilities: List[str] | None = None
    date_listed: date | None = None
    required_technologies: List[str] | None = None
    core_keywords: List[str] | None = None

    role_seniority_level: str | None = None
    years_of_experience_required: str | None = None
    minimum_education: str | None = None
    job_benefits: List[str] | None = None
    includes_equity: bool | None = None
    offers_visa_sponsorship: bool | None = None
    hiring_company_size: str | None = None
    hiring_industry: str | None = None
    source_listing_url: str | None = None
    full_raw_job_description: str | None = None

    @field_validator("date_listed", mode="before")
    @classmethod
    def normalize_missing_date(cls, value):
        if isinstance(value, str) and value.strip().lower() in {
            "",
            "n/a",
            "na",
            "none",
            "not provided",
            "not available",
            "unknown",
        }:
            return None
        return value


class JobList(BaseModel):
    jobs: List[Job]


class MatchedJob(BaseModel):
    job: Job
    match_score: int
    reason: str


class RankedJob(BaseModel):
    job: Job
    match_score: int
    reason: str


class RankedJobList(BaseModel):
    ranked_jobs: List[RankedJob]


class ChosenJob(BaseModel):
    job: Job
    selected: bool
    reason: str
