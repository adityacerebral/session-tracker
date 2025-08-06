# type: ignore
import uuid
from datetime import datetime, timedelta
from app.database import get_database
from app.config import settings
from app.models.models import (
    SessionDB, SessionRequest, SessionOperationRequest, SessionEvent, SessionStatus,
    PageTrackDB, PageTrackRequest, PageStats
)
from app.utils.utils import time_utils
from collections import defaultdict
from typing import Dict, List, Optional

class SessionService:
    def __init__(self):
        self.collection_name = settings.sessions_collection

    async def start_session(self, session_data: SessionRequest, user_id: Optional[str] = None):
        """Start a new session"""
        db = await get_database()
        collection = db[self.collection_name]
        
        parsed_time = time_utils.validate_and_parse_time(session_data.time)
        
        session_id = str(uuid.uuid4())
        
        session = SessionDB(
            session_id=session_id,
            username=session_data.user,
            created_at=datetime.utcnow(),
            events=[SessionEvent(
                timestamp=parsed_time,
                status=SessionStatus.ACTIVE,
                event_time=session_data.time
            )],
            status=SessionStatus.ACTIVE,
            app=session_data.app
        )
        
        await collection.insert_one(session.dict())
        return {
            "session_id": session_id,
            "user_id": session_data.user,
            "start_time": parsed_time,
            "message": "Session started successfully"
        }

    async def pause_session(self, session_data: SessionOperationRequest):
        """Pause an active session"""
        db = await get_database()
        collection = db[self.collection_name]
        
        session = await collection.find_one({
            "session_id": session_data.session_id,
            "status": SessionStatus.ACTIVE,
            "app": session_data.app
        })
        
        if not session:
            return {"error": "No active session found with the provided session ID"}
        
        parsed_time = time_utils.validate_and_parse_time(session_data.time)
        
        new_event = SessionEvent(
            timestamp=parsed_time,
            status=SessionStatus.PAUSED,
            event_time=session_data.time
        )
        
        active_time = await self._calculate_session_active_time(session['events'], new_event)
        
        await collection.update_one(
            {"session_id": session['session_id']},
            {
                "$push": {"events": new_event.dict()},
                "$set": {
                    "status": SessionStatus.PAUSED,
                    "total_active_time": active_time
                }
            }
        )
        
        return {
            "session_id": session_data.session_id,
            "message": "Session paused successfully",
            "timestamp": parsed_time
        }

    async def resume_session(self, session_data: SessionOperationRequest):
        """Resume a paused session"""
        db = await get_database()
        collection = db[self.collection_name]
        
        session = await collection.find_one({
            "session_id": session_data.session_id,
            "status": SessionStatus.PAUSED,
            "app": session_data.app
        })
        
        if not session:
            return {"error": "No paused session found with the provided session ID"}
        
        parsed_time = time_utils.validate_and_parse_time(session_data.time)
        
        new_event = SessionEvent(
            timestamp=parsed_time,
            status=SessionStatus.ACTIVE,
            event_time=session_data.time
        )
        
        await collection.update_one(
            {"session_id": session['session_id']},
            {
                "$push": {"events": new_event.dict()},
                "$set": {"status": SessionStatus.ACTIVE}
            }
        )
        
        return {
            "session_id": session_data.session_id,
            "message": "Session resumed successfully",
            "timestamp": parsed_time
        }

    async def end_session(self, session_data: SessionOperationRequest):
        """End an active or paused session"""
        db = await get_database()
        collection = db[self.collection_name]
        
        session = await collection.find_one({
            "session_id": session_data.session_id,
            "status": {"$in": [SessionStatus.ACTIVE, SessionStatus.PAUSED]},
            "app": session_data.app
        })
        
        if not session:
            return {"error": "No active or paused session found with the provided session ID"}
        
        parsed_time = time_utils.validate_and_parse_time(session_data.time)
        
        new_event = SessionEvent(
            timestamp=parsed_time,
            status=SessionStatus.ENDED,
            event_time=session_data.time
        )
        
        total_active_time = await self._calculate_session_active_time(session['events'], new_event)
        
        await collection.update_one(
            {"session_id": session['session_id']},
            {
                "$push": {"events": new_event.dict()},
                "$set": {
                    "status": SessionStatus.ENDED,
                    "ended_at": datetime.utcnow(),
                    "total_active_time": total_active_time
                }
            }
        )
        
        duration_str = time_utils.seconds_to_iso_duration(total_active_time)
        
        start_time = session['events'][0]['timestamp']
        
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        return {
            "session_id": session_data.session_id,
            "user_id": session['username'],
            "start_time": start_time,
            "end_time": parsed_time,
            "total_active_time": duration_str,
            "message": "Session ended successfully"
        }

    async def _calculate_session_active_time(self, events: List[dict], new_event: Optional[SessionEvent] = None) -> int:
        """Calculate total active time for a session"""
        if new_event:
            events = events + [new_event.dict()]
        
        total_active_seconds = 0
        last_active_start = None
        
        for event in events:
            event_time = event['timestamp'] if isinstance(event['timestamp'], datetime) else datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            status = event['status']
            
            if status == SessionStatus.ACTIVE:
                last_active_start = event_time
            elif status in [SessionStatus.PAUSED, SessionStatus.ENDED] and last_active_start:
                active_duration = (event_time - last_active_start).total_seconds()
                total_active_seconds += active_duration
                last_active_start = None
        
        return int(total_active_seconds)

    async def get_session_heatmap(self, app: str, user: Optional[str] = None) -> Dict:
        """Get session heatmap data - shows session counts per day for better visualization"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["username"] = user
        
        sessions = await collection.find(query_filter).to_list(None)
        
        # Count sessions by actual date
        daily_sessions = defaultdict(int)
        
        for session in sessions:
            if 'created_at' in session:
                # Get the actual date (YYYY-MM-DD format) for better visualization
                date_str = session['created_at'].strftime('%Y-%m-%d')
                daily_sessions[date_str] += 1
        
        # Convert to a more useful format for heatmap visualization
        # Return both the daily data and hourly breakdown for flexibility
        heatmap_data = {}
        
        # Daily sessions count (primary data for heatmap)
        daily_data = dict(daily_sessions)
        
        # Also include hourly breakdown by day of week for traditional heatmaps
        weekly_hourly = {}
        for day in range(7):  # 0-6 for Monday-Sunday
            weekly_hourly[str(day)] = {}
            for hour in range(24):  # 0-23 hours
                weekly_hourly[str(day)][str(hour)] = 0
        
        for session in sessions:
            if 'created_at' in session:
                day_of_week = session['created_at'].weekday()  # Monday is 0
                hour = session['created_at'].hour
                weekly_hourly[str(day_of_week)][str(hour)] += 1
        
        return {
            "heatmap_data": {
                "daily_sessions": daily_data,  # Date -> session count mapping
                "weekly_hourly": weekly_hourly,  # Day of week -> hour -> session count
                "total_sessions": len(sessions),
                "total_days_with_activity": len(daily_data),
                "date_range": {
                    "start_date": min(daily_data.keys()) if daily_data else None,
                    "end_date": max(daily_data.keys()) if daily_data else None
                }
            }
        }

    async def get_most_active(self, app: str, user: Optional[str] = None) -> Dict:
        """Get top 5 most active days with dates and most active hours for those days"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["username"] = user
        
        sessions = await collection.find(query_filter).to_list(None)
        
        # Count sessions by actual date and collect hours for each date
        date_counts = defaultdict(int)
        date_hours = defaultdict(lambda: defaultdict(int))
        
        # Day names mapping
        day_names = {
            0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
            4: "Friday", 5: "Saturday", 6: "Sunday"
        }
        
        for session in sessions:
            if 'created_at' in session:
                # Get the actual date (YYYY-MM-DD format)
                date_str = session['created_at'].strftime('%Y-%m-%d')
                day_of_week = session['created_at'].weekday()
                hour = session['created_at'].hour
                
                # Count sessions for this date
                date_counts[date_str] += 1
                
                # Count sessions for each hour on this date
                date_hours[date_str][hour] += 1
        
        # Get top 5 most active days
        most_active_dates = sorted(date_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Build the response with date, day name, count, and top hours for each day
        most_active_days = []
        for date_str, count in most_active_dates:
            # Parse the date to get day of week
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_of_week = date_obj.weekday()
            day_name = day_names[day_of_week]
            
            # Get hours for this specific date, sorted by count
            hours_for_date = sorted(date_hours[date_str].items(), key=lambda x: x[1], reverse=True)
            
            most_active_days.append({
                "date": date_str,
                "day": day_name,
                "count": count,
                "most_active_hours": [{"hour": hour, "count": hour_count} for hour, hour_count in hours_for_date]
            })
        
        return {
            "most_active_days": most_active_days
        }

    async def get_session_stats(self, app: str, user: Optional[str] = None) -> Dict:
        """Get session statistics"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["username"] = user
        
        sessions = await collection.find(query_filter).to_list(None)
        
        if not sessions:
            return {"total_users": 0, "avg_session_time": 0.0}
        
        unique_users = set()
        total_session_time = 0
        
        for session in sessions:
            unique_users.add(session['username'])
            total_session_time += session.get('total_active_time', 0)
        
        avg_session_time = total_session_time / len(sessions) / 60 if sessions else 0  # Convert to minutes
        
        return {
            "total_users": len(unique_users),
            "avg_session_time": round(avg_session_time, 2)
        }
        
    async def get_session_summary(self, app: str, user: Optional[str] = None) -> Dict:
        """Get summary of all sessions"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["username"] = user
        
        sessions = await collection.find(query_filter).to_list(None)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_sessions_time": "PT0S",
                "total_sessions_time_seconds": 0,
                "total_sessions_time_minutes": 0.0,
                "avg_sessions_time": "PT0S",
                "avg_sessions_time_seconds": 0.0,
                "avg_sessions_time_minutes": 0.0
            }
        
        total_sessions = len(sessions)
        total_sessions_time_seconds = sum(session.get('total_active_time', 0) for session in sessions)
        
        avg_sessions_time_seconds = total_sessions_time_seconds / total_sessions if total_sessions > 0 else 0
        
        total_sessions_time = time_utils.seconds_to_iso_duration(total_sessions_time_seconds)
        avg_sessions_time = time_utils.seconds_to_iso_duration(int(avg_sessions_time_seconds))
        
        return {
            "total_sessions": total_sessions,
            "total_sessions_time": total_sessions_time,
            "total_sessions_time_seconds": total_sessions_time_seconds,
            "total_sessions_time_minutes": round(total_sessions_time_seconds / 60, 2),
            "avg_sessions_time": avg_sessions_time,
            "avg_sessions_time_seconds": round(avg_sessions_time_seconds, 2),
            "avg_sessions_time_minutes": round(avg_sessions_time_seconds / 60, 2)
        }

    async def get_session_timeline(self, app: str, user: Optional[str] = None) -> Dict:
        """Get session timeline"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["username"] = user
        
        sessions = await collection.find(query_filter).sort("created_at", -1).to_list(None)
        
        timeline_items = []
        
        for session in sessions:
            active_time_seconds = session.get('total_active_time', 0)
            active_time_formatted = time_utils.seconds_to_iso_duration(active_time_seconds) if active_time_seconds else None
            
            timeline_items.append({
                "session_id": session['session_id'],
                "username": session['username'],
                "created_at": session['created_at'],
                "ended_at": session.get('ended_at'),
                "status": session['status'],
                "total_active_time_seconds": active_time_seconds,
                "total_active_time_formatted": active_time_formatted
            })
        
        return {
            "sessions": timeline_items,
            "total_count": len(timeline_items)
        }

    async def get_daily_time_spent(self, app: str, user: Optional[str] = None) -> Dict:
        """Get daily time spent for all sessions"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["username"] = user
        
        sessions = await collection.find(query_filter).to_list(None)
        
        daily_time = defaultdict(int)
        
        for session in sessions:
            if 'created_at' in session and 'total_active_time' in session:
                date_str = session['created_at'].strftime('%Y-%m-%d')
                daily_time[date_str] += session['total_active_time']
        
        result = []
        
        for date_str, total_seconds in sorted(daily_time.items()):
            result.append({
                "date": date_str,
                "total_time_seconds": total_seconds,
                "total_time_formatted": time_utils.seconds_to_iso_duration(total_seconds),
                "total_time_minutes": round(total_seconds / 60, 2)
            })
        
        return {
            "daily_time": result,
            "total_days": len(result)
        }
    
    async def get_time_by_page(self, app: str, user: Optional[str] = None) -> Dict:
        """Get time spent on each page"""
        db = await get_database()
        page_collection = db[settings.page_tracks_collection]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["user_id"] = user
        
        page_visits = await page_collection.find(query_filter).to_list(None)
        
        page_times = defaultdict(lambda: {"total_time": 0, "visit_count": 0})
        
        for visit in page_visits:
            page = visit['page']
            timespent = visit['timespent']
            
            page_times[page]["total_time"] += timespent
            page_times[page]["visit_count"] += 1
        
        result = []
        
        for page, data in sorted(page_times.items()):
            total_seconds = data["total_time"]
            result.append({
                "page": page,
                "total_time_seconds": total_seconds,
                "total_time_formatted": time_utils.seconds_to_iso_duration(total_seconds),
                "total_time_minutes": round(total_seconds / 60, 2),
                "visit_count": data["visit_count"]
            })
        
        return {
            "page_time": result,
            "total_pages": len(result)
        }
    
    async def get_session_timeline_detail(self, app: str, user: Optional[str] = None) -> Dict:
        """Get detailed session timeline including events"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["username"] = user
        
        sessions = await collection.find(query_filter).sort("created_at", -1).to_list(None)
        
        timeline_items = []
        
        for session in sessions:
            active_time_seconds = session.get('total_active_time', 0)
            active_time_formatted = time_utils.seconds_to_iso_duration(active_time_seconds) if active_time_seconds else None
            
            events = []
            for event in session.get('events', []):
                events.append({
                    "timestamp": event['timestamp'],
                    "status": event['status'],
                    "event_time": event['event_time']
                })
            
            timeline_items.append({
                "session_id": session['session_id'],
                "username": session['username'],
                "created_at": session['created_at'],
                "ended_at": session.get('ended_at'),
                "events": events,
                "status": session['status'],
                "total_active_time_seconds": active_time_seconds,
                "total_active_time_formatted": active_time_formatted
            })
        
        return {
            "sessions": timeline_items,
            "total_count": len(timeline_items)
        }

class PageService:
    def __init__(self):
        self.collection_name = settings.page_tracks_collection

    async def track_page(self, page_data: PageTrackRequest, user_id: Optional[str] = None):
        """Track page visit and time spent"""
        db = await get_database()
        collection = db[self.collection_name]
        
        page_track = PageTrackDB(
            page=page_data.page,
            timespent=page_data.timespent,
            timestamp=datetime.utcnow(),
            user_id=page_data.user,
            app=page_data.app
        )
        
        await collection.insert_one(page_track.dict())
        return page_track

    async def get_page_stats(self, app: str, user: Optional[str] = None):
        """Get page statistics"""
        db = await get_database()
        collection = db[self.collection_name]
        
        query_filter = {"app": app}
        
        if user and user.lower() != 'all':
            query_filter["user_id"] = user
        
        page_visits = await collection.find(query_filter).to_list(None)
        
        if not page_visits:
            return {
                "total_visits": 0,
                "unique_pages": 0,
                "page_stats": []
            }
        
        page_data = defaultdict(lambda: {"count": 0, "total_time": 0})
        
        for visit in page_visits:
            page = visit['page']
            timespent = visit['timespent']
            
            page_data[page]["count"] += 1
            page_data[page]["total_time"] += timespent
        
        page_stats = []
        
        for page, data in page_data.items():
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            
            page_stats.append(PageStats(
                page_id=page,
                visit_count=data["count"],
                avg_time_spent=round(avg_time, 2)
            ))
        
        return {
            "total_visits": len(page_visits),
            "unique_pages": len(page_data),
            "page_stats": page_stats
        }

# Create service instances
session_service = SessionService()
page_service = PageService() 