from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, List
import re


class URLCreate(BaseModel):
    url: str
    custom_code: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            v = "https://" + v
        return v

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v):
        if v is not None:
            if len(v) < 3 or len(v) > 20:
                raise ValueError("Custom code must be 3-20 characters")
            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError("Custom code can only contain letters, numbers, underscores, and hyphens")
        return v


class ClickResponse(BaseModel):
    id: int
    clicked_at: datetime
    country: Optional[str] = None
    referer: Optional[str] = None

    class Config:
        from_attributes = True


class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int
    short_url: Optional[str] = None

    class Config:
        from_attributes = True


class URLStatsResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int
    clicks: List[ClickResponse]
    clicks_by_day: dict
    top_referers: List[dict]

    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    name: str


class APIKeyResponse(BaseModel):
    id: int
    key: str
    name: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class QRCodeResponse(BaseModel):
    qr_code: str  # Base64 encoded PNG
