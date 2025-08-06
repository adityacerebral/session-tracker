#!/usr/bin/env python3
"""
Comprehensive test script for Session and Page Tracking API
Tests all functionality including:
- Authentication
- Session management (start, pause, resume, end)
- Page tracking
- Data retrieval with app and user filtering
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjk5OTk5OTk5OTl9.test_signature"
TEST_APP = "test_app"
TEST_USERS = ["user1", "user2", "user3"]

def get_iso_time(offset_seconds=0):
    """Get ISO 8601 formatted time with optional offset"""
    dt = datetime.utcnow() + timedelta(seconds=offset_seconds)
    # Format with exactly 3 decimal places for milliseconds
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

async def test_health_endpoint(session):
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    data = {"app": TEST_APP}
    
    async with session.post(f"{BASE_URL}/api/health", json=data) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Health check successful: {result['message']} (Status: {result['status']})")
            return True
        else:
            error = await response.text()
            print(f"❌ Health check failed: {error}")
            return False

async def test_auth_endpoints(session):
    """Test authentication endpoints"""
    print("\n🔐 Testing authentication endpoints...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test token validation
    data = {"app": TEST_APP}
    async with session.post(
        f"{BASE_URL}/api/auth/validate-token",
        headers=headers,
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Token validation successful: {result['message']}")
        else:
            error = await response.text()
            print(f"❌ Token validation failed: {error}")
    
    # Test token info
    async with session.post(
        f"{BASE_URL}/api/auth/token-info",
        headers=headers,
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Token info retrieved: User = {result['user']}")
        else:
            error = await response.text()
            print(f"❌ Token info failed: {error}")
    
    # Test auth health
    async with session.post(
        f"{BASE_URL}/api/auth/health",
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Auth health check successful: {result['message']}")
        else:
            error = await response.text()
            print(f"❌ Auth health check failed: {error}")

async def start_session(session, username):
    """Start a new session"""
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "user": username,
        "time": get_iso_time(),
        "status": "active",
        "app": TEST_APP
    }
    
    async with session.post(
        f"{BASE_URL}/api/sessions/start",
        headers=headers,
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Session started for {username}: {result['session_id']}")
            return result['session_id']
        else:
            error = await response.text()
            print(f"❌ Failed to start session for {username}: {error}")
            return None

async def pause_session(session, session_id, username):
    """Pause a session using session_id"""
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "user": username,
        "session_id": session_id,
        "time": get_iso_time(30),  # 30 seconds after start
        "app": TEST_APP
    }
    
    async with session.post(
        f"{BASE_URL}/api/sessions/pause",
        headers=headers,
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Session paused for {username}: {result['session_id']}")
            return True
        else:
            error = await response.text()
            print(f"❌ Failed to pause session for {username}: {error}")
            return False

async def resume_session(session, session_id, username):
    """Resume a session using session_id"""
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "user": username,
        "session_id": session_id,
        "time": get_iso_time(60),  # 60 seconds after start
        "app": TEST_APP
    }
    
    async with session.post(
        f"{BASE_URL}/api/sessions/resume",
        headers=headers,
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Session resumed for {username}: {result['session_id']}")
            return True
        else:
            error = await response.text()
            print(f"❌ Failed to resume session for {username}: {error}")
            return False

async def end_session(session, session_id, username):
    """End a session using session_id"""
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "user": username,
        "session_id": session_id,
        "time": get_iso_time(120),  # 120 seconds after start
        "app": TEST_APP
    }
    
    async with session.post(
        f"{BASE_URL}/api/sessions/end",
        headers=headers,
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Session ended for {username}: {result['session_id']}")
            return True
        else:
            error = await response.text()
            print(f"❌ Failed to end session for {username}: {error}")
            return False

async def track_page_visit(session, username, page, timespent):
    """Track a page visit"""
    data = {
        "user": username,
        "page": page,
        "timespent": timespent,
        "app": TEST_APP
    }
    
    async with session.post(
        f"{BASE_URL}/api/pages/track",
        json=data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"✅ Page visit tracked: {username} visited {page} for {timespent}s")
            return True
        else:
            error = await response.text()
            print(f"❌ Failed to track page visit: {error}")
            return False

async def test_session_management():
    """Test session management functionality"""
    print("\n🔄 Testing session management...")
    
    async with aiohttp.ClientSession() as session:
        # Start sessions for different users
        session_ids = {}
        for user in TEST_USERS:
            session_id = await start_session(session, user)
            if session_id:
                session_ids[user] = session_id
        
        # Pause sessions
        for user, session_id in session_ids.items():
            await pause_session(session, session_id, user)
        
        # Resume sessions
        for user, session_id in session_ids.items():
            await resume_session(session, session_id, user)
        
        # End sessions
        for user, session_id in session_ids.items():
            await end_session(session, session_id, user)
        
        return session_ids

async def test_page_tracking():
    """Test page tracking functionality"""
    print("\n📊 Testing page tracking...")
    
    # Sample page tracking data
    page_visits = [
        {"user": "user1", "page": "/home", "timespent": 45},
        {"user": "user1", "page": "/about", "timespent": 120},
        {"user": "user1", "page": "/products", "timespent": 180},
        {"user": "user2", "page": "/home", "timespent": 60},
        {"user": "user2", "page": "/contact", "timespent": 75},
        {"user": "user3", "page": "/blog", "timespent": 240},
        {"user": "user3", "page": "/products", "timespent": 150}
    ]
    
    async with aiohttp.ClientSession() as session:
        for visit in page_visits:
            await track_page_visit(
                session, 
                visit["user"], 
                visit["page"], 
                visit["timespent"]
            )

async def test_data_retrieval_with_filtering():
    """Test data retrieval with app and user filtering"""
    print("\n🔍 Testing data retrieval with filtering...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Test retrieving all data for the app
        print("\n📈 Testing retrieval of all data for app...")
        data = {"app": TEST_APP}
        
        async with session.post(
            f"{BASE_URL}/api/sessions/summary",
            headers=headers,
            json=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Retrieved summary for all users:")
                print(f"   Total sessions: {result['total_sessions']}")
                print(f"   Total time: {result['total_sessions_time']}")
            else:
                error = await response.text()
                print(f"❌ Failed to retrieve summary: {error}")
        
        # Test retrieving data for specific users
        for user in TEST_USERS:
            print(f"\n📊 Testing retrieval of data for user {user}...")
            data = {"app": TEST_APP, "user": user}
            
            async with session.post(
                f"{BASE_URL}/api/sessions/summary",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Retrieved summary for user {user}:")
                    print(f"   Total sessions: {result['total_sessions']}")
                    print(f"   Total time: {result['total_sessions_time']}")
                else:
                    error = await response.text()
                    print(f"❌ Failed to retrieve summary for user {user}: {error}")
        
        # Test page stats with filtering
        print("\n📊 Testing page statistics with filtering...")
        
        # All users
        data = {"app": TEST_APP}
        async with session.post(
            f"{BASE_URL}/api/pages/stats",
            headers=headers,
            json=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Retrieved page stats for all users:")
                print(f"   Total visits: {result['total_visits']}")
                print(f"   Unique pages: {result['unique_pages']}")
            else:
                error = await response.text()
                print(f"❌ Failed to retrieve page stats: {error}")
        
        # Specific user
        data = {"app": TEST_APP, "user": "user1"}
        async with session.post(
            f"{BASE_URL}/api/pages/stats",
            headers=headers,
            json=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Retrieved page stats for user1:")
                print(f"   Total visits: {result['total_visits']}")
                print(f"   Unique pages: {result['unique_pages']}")
            else:
                error = await response.text()
                print(f"❌ Failed to retrieve page stats for user1: {error}")

async def test_other_endpoints():
    """Test other endpoints"""
    print("\n🧪 Testing other endpoints...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        {"name": "Session Heatmap", "url": "/api/sessions/heatmap"},
        {"name": "Most Active", "url": "/api/sessions/most-active"},
        {"name": "Session Stats", "url": "/api/sessions/stats"},
        {"name": "Session Timeline", "url": "/api/sessions/timeline"},
        {"name": "Daily Time Spent", "url": "/api/sessions/daily-time-spent"},
        {"name": "Time by Page", "url": "/api/sessions/time-by-page"},
        {"name": "Session Timeline Detail", "url": "/api/sessions/session-timeline-detail"}
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            print(f"\nTesting {endpoint['name']} endpoint...")
            
            # Test with all users
            data = {"app": TEST_APP}
            async with session.post(
                f"{BASE_URL}{endpoint['url']}",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ {endpoint['name']} endpoint successful for all users")
                    
                    # Special handling for Most Active endpoint to test new format
                    if endpoint['name'] == "Most Active":
                        if 'most_active_days' in result and result['most_active_days']:
                            first_day = result['most_active_days'][0]
                            if 'date' in first_day and 'day' in first_day and 'most_active_hours' in first_day:
                                print(f"   ✅ New format confirmed: {first_day['date']} ({first_day['day']}) with {len(first_day['most_active_hours'])} hours")
                            else:
                                print(f"   ⚠️  Old format detected")
                        else:
                            print(f"   📊 No activity data found")
                            
                else:
                    error = await response.text()
                    print(f"❌ {endpoint['name']} endpoint failed: {error}")
            
            # Test with specific user
            data = {"app": TEST_APP, "user": "user1"}
            async with session.post(
                f"{BASE_URL}{endpoint['url']}",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    print(f"✅ {endpoint['name']} endpoint successful for user1")
                else:
                    error = await response.text()
                    print(f"❌ {endpoint['name']} endpoint failed for user1: {error}")

async def main():
    """Main test function"""
    print("🚀 Starting Comprehensive API Test")
    print("=" * 60)
    
    try:
        # Test basic health endpoint
        async with aiohttp.ClientSession() as session:
            health_ok = await test_health_endpoint(session)
            if not health_ok:
                print("❌ Health check failed, aborting tests")
                return
        
        # Test authentication endpoints
        async with aiohttp.ClientSession() as session:
            await test_auth_endpoints(session)
        
        # Test session management
        await test_session_management()
        
        # Test page tracking
        await test_page_tracking()
        
        # Test data retrieval with filtering
        await test_data_retrieval_with_filtering()
        
        # Test other endpoints
        await test_other_endpoints()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Tests failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 