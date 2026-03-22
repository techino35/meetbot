from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class JobStatus(str, Enum):
    pending = "pending"
    transcribing = "transcribing"
    structuring = "structuring"
    writing = "writing"
    done = "done"
    failed = "failed"


class ActionItem(BaseModel):
    owner: str
    action: str
    deadline: str


class MeetingStructure(BaseModel):
    summary: list[str]
    discussion_points: list[str]
    action_items: list[ActionItem]
    decisions: list[str]


class Job(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.pending
    filename: str = ""
    transcript: Optional[str] = None
    structure: Optional[MeetingStructure] = None
    doc_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UploadResponse(BaseModel):
    job_id: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    doc_url: Optional[str] = None
    error: Optional[str] = None
    structure: Optional[MeetingStructure] = None
