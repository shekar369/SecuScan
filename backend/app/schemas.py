from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime

class WebsiteCreate(BaseModel):
    url: HttpUrl
    name: Optional[str] = None

class Website(BaseModel):
    id: UUID
    url: HttpUrl
    name: Optional[str]
    created_at: datetime
    last_scanned_at: Optional[datetime]

    class Config:
        orm_mode = True

class ScanRunBase(BaseModel):
    status: Optional[str]
    report_path: Optional[str]
    parsed_result: Optional[dict]

class ScanRunCreate(BaseModel):
    website_id: UUID

class ScanRun(ScanRunBase):
    id: UUID
    website_id: UUID
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
