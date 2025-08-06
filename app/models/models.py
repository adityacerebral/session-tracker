from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from app.utils.utils import time_utils

# Session Models
class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"

class SessionRequest(BaseModel):
    user: str
    time: str
    status: str
    app: str
    
    @validator('time')
    def validate_time_format(cls, v):
        """Validate that time is in correct ISO 8601 format"""
        if not time_utils.validate_iso_time_format(v):
            raise ValueError(f"Invalid time format. Expected ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ), got: {v}")
        return v
    
    @validator('user')
    def validate_user(cls, v):
        """Validate user is not empty"""
        if not v or not v.strip():
            raise ValueError("User cannot be empty")
        return v.strip()

class SessionOperationRequest(BaseModel):
    user: str
    session_id: str
    time: str
    app: str
    
    @validator('time')
    def validate_time_format(cls, v):
        """Validate that time is in correct ISO 8601 format"""
        if not time_utils.validate_iso_time_format(v):
            raise ValueError(f"Invalid time format. Expected ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ), got: {v}")
        return v
    
    @validator('user')
    def validate_user(cls, v):
        """Validate user is not empty"""
        if not v or not v.strip():
            raise ValueError("User cannot be empty")
        return v.strip()
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """Validate session_id is not empty"""
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()

class SessionStartResponse(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime
    message: str = "Session started successfully"

class SessionOperationResponse(BaseModel):
    session_id: str
    message: str
    timestamp: datetime

class SessionEndResponse(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    total_active_time: str  # ISO 8601 duration format
    message: str = "Session ended successfully"

class SessionEvent(BaseModel):
    timestamp: datetime
    status: SessionStatus
    event_time: str  # time from user

class SessionDB(BaseModel):
    session_id: str
    username: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    events: List[SessionEvent] = []
    total_active_time: int = 0  # in seconds
    status: SessionStatus = SessionStatus.ACTIVE
    app: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HeatmapDateRange(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class HeatmapData(BaseModel):
    daily_sessions: Dict[str, int]  # Date -> session count mapping
    weekly_hourly: Dict[str, Dict[str, int]]  # Day of week -> hour -> session count
    total_sessions: int
    total_days_with_activity: int
    date_range: HeatmapDateRange

class SessionHeatmapResponse(BaseModel):
    heatmap_data: HeatmapData

class SessionMostActiveResponse(BaseModel):
    most_active_days: List[dict]

class SessionStatsResponse(BaseModel):
    total_users: int
    avg_session_time: float  # in minutes
    
class SessionSummaryResponse(BaseModel):
    total_sessions: int
    total_sessions_time: str  # ISO 8601 duration format
    total_sessions_time_seconds: int  # Raw seconds
    total_sessions_time_minutes: float  # Time in minutes
    avg_sessions_time: str  # ISO 8601 duration format
    avg_sessions_time_seconds: float  # Raw seconds
    avg_sessions_time_minutes: float  # Time in minutes

class SessionTimelineItem(BaseModel):
    session_id: str
    username: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    status: SessionStatus
    total_active_time_seconds: Optional[int] = None
    total_active_time_formatted: Optional[str] = None  # ISO 8601 duration format
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SessionTimelineResponse(BaseModel):
    sessions: List[SessionTimelineItem]
    total_count: int

# Page Tracking Models
class PageTrackRequest(BaseModel):
    user: str
    page: str
    timespent: int  # in seconds
    app: str
    
    @validator('user')
    def validate_user(cls, v):
        """Validate user is not empty"""
        if not v or not v.strip():
            raise ValueError("User cannot be empty")
        return v.strip()

class PageTrackResponse(BaseModel):
    message: str
    page: str
    timespent: int
    timestamp: datetime

class PageStats(BaseModel):
    page_id: str
    visit_count: int
    avg_time_spent: float  # in seconds

class PageStatsResponse(BaseModel):
    total_visits: int
    unique_pages: int
    page_stats: List[PageStats]

class PageTrackDB(BaseModel):
    page: str
    timespent: int
    timestamp: datetime
    user_id: Optional[str] = None
    app: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Auth Models
class TokenValidationResponse(BaseModel):
    valid: bool
    user: str
    message: str

class TokenInfoResponse(BaseModel):
    user: str
    payload: Dict[str, Any]
    message: str 

# New response models for the requested endpoints
class DailyTimeSpentItem(BaseModel):
    date: str
    total_time_seconds: int
    total_time_formatted: str  # ISO 8601 duration format
    total_time_minutes: float

class DailyTimeSpentResponse(BaseModel):
    daily_time: List[DailyTimeSpentItem]
    total_days: int

class TimeByPageItem(BaseModel):
    page: str
    total_time_seconds: int
    total_time_formatted: str  # ISO 8601 duration format
    total_time_minutes: float
    visit_count: int

class TimeByPageResponse(BaseModel):
    page_time: List[TimeByPageItem]
    total_pages: int

class SessionTimelineDetailItem(BaseModel):
    session_id: str
    username: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    events: List[Dict[str, Any]]
    status: SessionStatus
    total_active_time_seconds: Optional[int] = None
    total_active_time_formatted: Optional[str] = None  # ISO 8601 duration format
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SessionTimelineDetailResponse(BaseModel):
    sessions: List[SessionTimelineDetailItem]
    total_count: int 

# Request model for GET endpoints converted to POST
class AppRequest(BaseModel):
    app: str
    user: Optional[str] = None 