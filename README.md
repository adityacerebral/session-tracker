# Session and Page Tracking Backend

A FastAPI backend for tracking user sessions and page visits with MongoDB storage.

## Features

- **Page Tracking**: Track page visits and time spent on each page
- **Session Management**: Start, pause, resume, and end user sessions
- **Analytics**: Get statistics, heatmaps, and insights from tracking data
- **Async Operations**: Built with FastAPI and Motor for async MongoDB operations
- **Time Validation**: Robust ISO 8601 time format validation and parsing utilities
- **JWT Authentication**: Secure API endpoints with Bearer token authentication
- **App-specific Data**: All data is segregated by app identifier
- **User Filtering**: Optional user filtering for all retrieval endpoints

## Project Structure

```
session_server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── page_track.py    # Page tracking models
│   │   └── session.py       # Session tracking models
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── page_service.py  # Page tracking service
│   │   └── session_service.py # Session tracking service
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   ├── time_utils.py    # Time validation and parsing utilities
│   │   ├── auth_utils.py    # JWT authentication utilities
│   │   └── jwt_helper.py    # JWT token parsing helpers
│   └── api/                 # API routes
│       ├── __init__.py
│       ├── auth_routes.py   # Authentication endpoints
│       ├── page_routes.py   # Page tracking endpoints
│       └── session_routes.py # Session tracking endpoints
├── requirements.txt
├── .env
└── README.md
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB**:
   - Install MongoDB locally or use MongoDB Atlas
   - Update the `.env` file with your MongoDB connection string

3. **Environment Variables**:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=session_tracker
   JWT_SECRET_KEY=your-secret-key-change-this-in-production
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Authentication

All API endpoints (except health checks) require JWT authentication via Bearer token.

**Authentication Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Format:** JWT tokens must contain:
- `sub` (subject) - Username or user ID
- `exp` (expiration) - Token expiration timestamp

**Flexible Token Validation:**
The system supports tokens signed with different secret keys by:
1. First attempting signature verification with the configured secret
2. If that fails, extracting user info from the payload without verification
3. Always checking token expiration regardless of signature validation

## Important API Changes

All endpoints now:
1. Use POST method (even for retrieving data)
2. Require an `app` field in the request body
3. Return only data specific to the provided app
4. Support optional user filtering with the `user` field

### Data Filtering

- **App Filtering**: Required for all endpoints. Only data for the specified app will be returned.
- **User Filtering**: Optional for all retrieval endpoints. When provided, only data for the specified user will be returned.
  - If `user` is not provided or set to `"all"`, data for all users within the app will be returned.

### Example Request:

```json
POST /api/sessions/summary
{
  "app": "myapp",
  "user": "john.doe@example.com"
}
```

To get data for all users within an app:

```json
POST /api/sessions/summary
{
  "app": "myapp",
  "user": "all"
}
```

Or simply omit the user field:

```json
POST /api/sessions/summary
{
  "app": "myapp"
}
```

### Authentication Endpoints

#### POST `/api/v1/auth/validate-token`
Validate the provided JWT token.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "app": "myapp"
}
```

**Response:**
```json
{
  "valid": true,
  "user": "Demo",
  "message": "Token is valid"
}
```

#### POST `/api/v1/auth/token-info`
Get detailed token information.

**Request Body:**
```json
{
  "app": "myapp"
}
```

**Response:**
```json
{
  "user": "Demo",
  "payload": {"sub": "Demo", "exp": 1751046357},
  "message": "Token information retrieved successfully"
}
```

## API Endpoints

### Page Tracking

#### 1. POST `/api/v1/page_track`
Track a page visit and time spent.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body**:
```json
{
  "page": "string",
  "timespent": 120
}
```

**Response**:
```json
{
  "message": "Page tracked successfully",
  "page": "string",
  "timespent": 120,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 2. GET `/api/v1/page_stats`
Get page statistics including visit counts and time spent.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response**:
```json
{
  "page_counts": {
    "homepage": 150,
    "about": 75
  },
  "time_spent": {
    "last_24hr": {"homepage": 3600, "about": 1800},
    "last_7days": {"homepage": 25200, "about": 12600},
    "last_1month": {"homepage": 108000, "about": 54000},
    "all_time": {"homepage": 216000, "about": 108000}
  }
}
```

### Session Tracking

#### 3. POST `/api/v1/session_start`
Start a new user session.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body**:
```json
{
  "username": "john_doe",
  "time": "2024-01-01T12:00:00Z",
  "status": "active"
}
```

**Response**:
```json
{
  "session_id": "uuid-string",
  "message": "Session started successfully"
}
```

#### 4. POST `/api/v1/session_pause`
Pause an active session.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body**:
```json
{
  "username": "john_doe",
  "time": "2024-01-01T12:30:00Z",
  "status": "paused"
}
```

**Response**:
```json
{
  "message": "Session paused successfully"
}
```

#### 5. POST `/api/v1/session_resume`
Resume a paused session.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body**:
```json
{
  "username": "john_doe",
  "time": "2024-01-01T12:45:00Z",
  "status": "active"
}
```

**Response**:
```json
{
  "message": "Session resumed successfully"
}
```

#### 6. POST `/api/v1/session_end`
End an active or paused session.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body**:
```json
{
  "username": "john_doe",
  "time": "2024-01-01T13:00:00Z",
  "status": "ended"
}
```

**Response**:
```json
{
  "message": "Session ended successfully"
}
```

#### 7. GET `/api/v1/session_heatmap`
Get session heatmap data for the last 30 days.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response**:
```json
{
  "heatmap_data": {
    "daily_sessions": {
      "2024-01-01": 5,
      "2024-01-02": 12,
      "2024-01-03": 8
    },
    "weekly_hourly": {
      "0": {
        "9": 5,
        "10": 12,
        "11": 8
      },
      "1": {
        "9": 3,
        "10": 15,
        "11": 10
      }
    },
    "total_sessions": 25,
    "total_days_with_activity": 3,
    "date_range": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-03"
    }
  }
}
```

#### 8. GET `/api/v1/session_most_active`
Get most active days and hours.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response**:
```json
{
  "most_active_days": [
    {
      "date": "2024-01-15",
      "day": "Monday",
      "count": 42,
      "most_active_hours": [
        {"hour": 10, "count": 15},
        {"hour": 14, "count": 12},
        {"hour": 9, "count": 8}
      ]
    },
    {
      "date": "2024-01-17",
      "day": "Wednesday", 
      "count": 38,
      "most_active_hours": [
        {"hour": 11, "count": 14},
        {"hour": 15, "count": 10},
        {"hour": 13, "count": 7}
      ]
    }
  ]
}
```

#### 9. GET `/api/v1/session_stats`
Get session statistics for the last 30 days.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response**:
```json
{
  "total_users": 25,
  "avg_session_time": 45.5
}
```

## Session Time Calculation Logic

The system tracks session active time by:

1. **Session Start**: Records the start timestamp
2. **Session Pause**: Calculates time from last active point and adds to total
3. **Session Resume**: Starts counting time again from resume point
4. **Session End**: Calculates final active time and stores total

The `total_active_time` field stores the cumulative active seconds, excluding paused periods.

## Time Format Validation

The system includes comprehensive time validation utilities that ensure all time strings follow the ISO 8601 format:

**Accepted Time Formats:**
- `"2024-01-01T12:00:00Z"` - Standard ISO with timezone
- `"2024-01-01T12:00:00.123Z"` - With milliseconds
- `"2024-01-01T12:00:00"` - Without timezone indicator

**Time Utilities Features:**
- **Format Validation**: Validates ISO 8601 format using regex
- **Parsing**: Converts time strings to Python datetime objects
- **Separation**: Extracts date and time components separately
- **Hour Extraction**: Gets hour component for analytics
- **Time Difference**: Calculates seconds between two timestamps
- **Error Handling**: Provides clear error messages for invalid formats

**Usage Example:**
```python
from app.utils.time_utils import time_utils

# Validate format
is_valid = time_utils.validate_iso_time_format("2024-01-01T12:00:00Z")

# Parse to datetime
dt = time_utils.parse_iso_time_string("2024-01-01T12:00:00Z")

# Separate components
date, time = time_utils.separate_date_and_time("2024-01-01T12:00:00Z")
# Returns: ("2024-01-01", "12:00:00")

# Get hour for analytics
hour = time_utils.get_hour_from_time_string("2024-01-01T12:00:00Z")
# Returns: 12
```

## Database Collections

### page_tracks
```json
{
  "_id": "ObjectId",
  "page": "string",
  "timespent": "number",
  "timestamp": "datetime"
}
```

### sessions
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "username": "string",
  "created_at": "datetime",
  "ended_at": "datetime",
  "events": [
    {
      "timestamp": "datetime",
      "status": "active|paused|ended",
      "event_time": "string"
    }
  ],
  "total_active_time": "number",
  "status": "active|paused|ended"
}
```

## Development

To run in development mode:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

You can test the APIs using the interactive documentation at `/docs` or with curl:

```bash
# Validate token
curl -X GET "http://localhost:8000/api/v1/auth/validate-token" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Track a page (with authentication)
curl -X POST "http://localhost:8000/api/v1/page_track" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -d '{"page": "homepage", "timespent": 120}'

# Start a session (with authentication)
curl -X POST "http://localhost:8000/api/v1/session_start" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -d '{"username": "test_user", "time": "2024-01-01T12:00:00Z", "status": "active"}'

# Test utilities
python test_time_utils.py
python test_auth.py
``` 