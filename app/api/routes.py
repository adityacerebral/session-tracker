from fastapi import APIRouter, HTTPException, Depends
from app.models.models import (
    SessionRequest, SessionOperationRequest, SessionStartResponse, 
    SessionOperationResponse, SessionEndResponse,
    SessionHeatmapResponse, SessionMostActiveResponse, SessionStatsResponse,
    SessionSummaryResponse, SessionTimelineResponse,
    PageTrackRequest, PageTrackResponse, PageStatsResponse,
    TokenValidationResponse, TokenInfoResponse,
    DailyTimeSpentResponse, TimeByPageResponse, SessionTimelineDetailResponse,
    AppRequest
)
from app.services.services import session_service, page_service
from app.utils.utils import get_current_user
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

# Auth Router
auth_router = APIRouter()

@auth_router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Validate the provided JWT token and return user information"""
    return TokenValidationResponse(
        valid=True,
        user=current_user,
        message="Token is valid"
    )

@auth_router.post("/token-info", response_model=TokenInfoResponse)
async def get_token_info(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get detailed information from the JWT token"""
    return TokenInfoResponse(
        user=current_user,
        payload={"sub": current_user, "note": "Full payload not available from dependency"},
        message="Token information retrieved successfully"
    )

@auth_router.post("/health")
async def auth_health(app_data: AppRequest):
    """Public health check endpoint (no authentication required)"""
    return {
        "status": "healthy",
        "service": "authentication",
        "message": "Auth service is running",
        "app": app_data.app
    }

# Session Router
session_router = APIRouter()

@session_router.post("/start", response_model=SessionStartResponse)
async def start_session(session_data: SessionRequest, current_user: str = Depends(get_current_user)):
    """Start a new session"""
    try:
        result = await session_service.start_session(session_data, session_data.user)
        return SessionStartResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")

@session_router.post("/pause", response_model=SessionOperationResponse)
async def pause_session(session_data: SessionOperationRequest, current_user: str = Depends(get_current_user)):
    """Pause an active session using session_id"""
    try:
        result = await session_service.pause_session(session_data)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return SessionOperationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pausing session: {str(e)}")

@session_router.post("/resume", response_model=SessionOperationResponse)
async def resume_session(session_data: SessionOperationRequest, current_user: str = Depends(get_current_user)):
    """Resume a paused session using session_id"""
    try:
        result = await session_service.resume_session(session_data)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return SessionOperationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resuming session: {str(e)}")

@session_router.post("/end", response_model=SessionEndResponse)
async def end_session(session_data: SessionOperationRequest, current_user: str = Depends(get_current_user)):
    """End an active or paused session using session_id"""
    try:
        result = await session_service.end_session(session_data)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return SessionEndResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending session: {str(e)}")

@session_router.post("/heatmap", response_model=SessionHeatmapResponse)
async def get_session_heatmap(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get session heatmap data"""
    try:
        heatmap_data = await session_service.get_session_heatmap(app_data.app, app_data.user)
        return SessionHeatmapResponse(**heatmap_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session heatmap: {str(e)}")

@session_router.post("/most-active", response_model=SessionMostActiveResponse)
async def get_most_active(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get most active days and hours"""
    try:
        active_data = await session_service.get_most_active(app_data.app, app_data.user)
        return SessionMostActiveResponse(**active_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting most active data: {str(e)}")

@session_router.post("/stats", response_model=SessionStatsResponse)
async def get_session_stats(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get session statistics"""
    try:
        stats = await session_service.get_session_stats(app_data.app, app_data.user)
        return SessionStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session stats: {str(e)}")
        
@session_router.post("/summary", response_model=SessionSummaryResponse)
async def get_session_summary(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get summary of all sessions including total count, time and averages"""
    try:
        summary = await session_service.get_session_summary(app_data.app, app_data.user)
        return SessionSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session summary: {str(e)}")
        
@session_router.post("/public-summary", response_model=SessionSummaryResponse)
async def get_public_session_summary(app_data: AppRequest):
    """Get summary of all sessions including total count, time and averages (public)"""
    try:
        summary = await session_service.get_session_summary(app_data.app, app_data.user)
        return SessionSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session summary: {str(e)}")

@session_router.post("/timeline", response_model=SessionTimelineResponse)
async def get_session_timeline(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get session timeline showing when sessions were created and ended"""
    try:
        timeline = await session_service.get_session_timeline(app_data.app, app_data.user)
        return SessionTimelineResponse(**timeline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session timeline: {str(e)}")

@session_router.post("/public-timeline", response_model=SessionTimelineResponse)
async def get_public_session_timeline(app_data: AppRequest):
    """Get session timeline showing when sessions were created and ended (public)"""
    try:
        timeline = await session_service.get_session_timeline(app_data.app, app_data.user)
        return SessionTimelineResponse(**timeline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session timeline: {str(e)}")

@session_router.post("/daily-time-spent", response_model=DailyTimeSpentResponse)
async def get_daily_time_spent(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get daily time spent for all sessions"""
    try:
        daily_time = await session_service.get_daily_time_spent(app_data.app, app_data.user)
        return DailyTimeSpentResponse(**daily_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting daily time spent: {str(e)}")

@session_router.post("/time-by-page", response_model=TimeByPageResponse)
async def get_time_by_page(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get time spent on each page"""
    try:
        page_time = await session_service.get_time_by_page(app_data.app, app_data.user)
        return TimeByPageResponse(**page_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting time by page: {str(e)}")

@session_router.post("/session-timeline-detail", response_model=SessionTimelineDetailResponse)
async def get_session_timeline_detail(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get detailed session timeline including events"""
    try:
        timeline = await session_service.get_session_timeline_detail(app_data.app, app_data.user)
        return SessionTimelineDetailResponse(**timeline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session timeline detail: {str(e)}")

# Page Router
page_router = APIRouter()

@page_router.post("/track", response_model=PageTrackResponse)
async def track_page(page_data: PageTrackRequest):
    """Track page visit and time spent"""
    try:
        result = await page_service.track_page(page_data, page_data.user)
        return PageTrackResponse(
            message="Page visit tracked successfully",
            page=result.page,
            timespent=result.timespent,
            timestamp=result.timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking page: {str(e)}")

@page_router.post("/stats", response_model=PageStatsResponse)
async def get_page_stats(app_data: AppRequest, current_user: str = Depends(get_current_user)):
    """Get page statistics including visit counts and average time spent"""
    try:
        stats = await page_service.get_page_stats(app_data.app, app_data.user)
        return PageStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting page stats: {str(e)}") 