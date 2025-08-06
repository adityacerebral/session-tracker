# Session Server API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Common Response Format](#common-response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Session Management Endpoints](#session-management-endpoints)
  - [Page Tracking Endpoints](#page-tracking-endpoints)
  - [Health Check Endpoints](#health-check-endpoints)

## Overview

The Session Server API is a RESTful service for tracking user sessions, page visits, and generating analytics data. It provides comprehensive session management capabilities including start, pause, resume, and end operations, along with detailed analytics and reporting features.

## Authentication

Most endpoints require JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

**Note**: Some endpoints are marked as public and don't require authentication.

## Base URL

```
http://localhost:8000
```

## Common Response Format

All API responses follow a consistent JSON format:

```json
{
  "status": "success|error",
  "message": "Response message",
  "data": { ... }
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid or missing token)
- `404` - Not Found
- `422` - Unprocessable Entity (validation errors)
- `500` - Internal Server Error

Error responses include detailed error messages:

```json
{
  "status": "error",
  "message": "Error description",
  "details": "Additional error details"
}
```

## Endpoints

### Authentication Endpoints

#### Validate Token
**POST** `/api/auth/validate-token`

Validates the provided JWT token and returns user information.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Token is valid",
  "data": {
    "user": "username",
    "app": "your_app_name",
    "token_info": { ... }
  }
}
```

#### Get Token Information
**POST** `/api/auth/token-info`

Gets detailed information from the JWT token.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Token information retrieved",
  "data": {
    "sub": "username",
    "exp": 1751046357,
    "app": "your_app_name"
  }
}
```

#### Authentication Health Check
**POST** `/api/auth/health`

Public health check endpoint for authentication service.

**Authentication Required**: No

**Request Body**:
```json
{
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Authentication service is healthy"
}
```

### Session Management Endpoints

#### Start Session
**POST** `/api/sessions/start`

Starts a new user session.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "user": "username",
  "time": "2024-01-01T12:00:00.000Z",
  "status": "active",
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Session started successfully",
  "data": {
    "session_id": "uuid-string",
    "user": "username",
    "start_time": "2024-01-01T12:00:00.000Z",
    "status": "active"
  }
}
```

#### Pause Session
**POST** `/api/sessions/pause`

Pauses an active session.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "user": "username",
  "session_id": "uuid-string",
  "time": "2024-01-01T12:30:00.000Z",
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Session paused successfully",
  "data": {
    "session_id": "uuid-string",
    "status": "paused",
    "pause_time": "2024-01-01T12:30:00.000Z"
  }
}
```

#### Resume Session
**POST** `/api/sessions/resume`

Resumes a paused session.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "user": "username",
  "session_id": "uuid-string",
  "time": "2024-01-01T12:45:00.000Z",
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Session resumed successfully",
  "data": {
    "session_id": "uuid-string",
    "status": "active",
    "resume_time": "2024-01-01T12:45:00.000Z"
  }
}
```

#### End Session
**POST** `/api/sessions/end`

Ends an active or paused session.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "user": "username",
  "session_id": "uuid-string",
  "time": "2024-01-01T13:00:00.000Z",
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Session ended successfully",
  "data": {
    "session_id": "uuid-string",
    "status": "ended",
    "end_time": "2024-01-01T13:00:00.000Z",
    "total_duration": "01:00:00"
  }
}
```

#### Get Session Heatmap
**POST** `/api/sessions/heatmap`

Retrieves session heatmap data showing activity patterns.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "heatmap_data": {
    "daily_sessions": {
      "2024-01-15": 5,
      "2024-01-16": 12,
      "2024-01-17": 8
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
      "start_date": "2024-01-15",
      "end_date": "2024-01-17"
    }
  }
}
```

#### Get Most Active Times
**POST** `/api/sessions/most-active`

Gets the most active days and hours based on session data.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "most_active_day": "Monday",
    "most_active_hour": 14,
    "peak_sessions": 25
  }
}
```

#### Get Session Statistics
**POST** `/api/sessions/stats`

Retrieves comprehensive session statistics.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_sessions": 150,
    "average_session_duration": "00:45:30",
    "total_time_spent": "112:15:00",
    "active_days": 45
  }
}
```

#### Get Session Summary
**POST** `/api/sessions/summary`

Gets a summary of all sessions including totals and averages.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_sessions": 150,
    "total_duration": "112:15:00",
    "average_duration": "00:45:30",
    "longest_session": "02:30:45",
    "shortest_session": "00:05:12"
  }
}
```

#### Get Public Session Summary
**POST** `/api/sessions/public-summary`

Public version of session summary (no authentication required).

**Authentication Required**: No

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**: Same as `/api/sessions/summary`

#### Get Session Timeline
**POST** `/api/sessions/timeline`

Retrieves session timeline showing when sessions were created and ended.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "timeline": [
      {
        "session_id": "uuid-1",
        "start_time": "2024-01-01T09:00:00.000Z",
        "end_time": "2024-01-01T10:30:00.000Z",
        "duration": "01:30:00"
      }
    ]
  }
}
```

#### Get Public Session Timeline
**POST** `/api/sessions/public-timeline`

Public version of session timeline (no authentication required).

**Authentication Required**: No

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**: Same as `/api/sessions/timeline`

#### Get Daily Time Spent
**POST** `/api/sessions/daily-time-spent`

Retrieves daily time spent across all sessions.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "daily_time": {
      "2024-01-01": "02:30:00",
      "2024-01-02": "03:15:00",
      "2024-01-03": "01:45:00"
    }
  }
}
```

#### Get Time by Page
**POST** `/api/sessions/time-by-page`

Gets time spent on each page across all sessions.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "page_time": {
      "/dashboard": "05:30:00",
      "/profile": "02:15:00",
      "/settings": "01:10:00"
    }
  }
}
```

#### Get Detailed Session Timeline
**POST** `/api/sessions/session-timeline-detail`

Retrieves detailed session timeline including all events.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "detailed_timeline": [
      {
        "session_id": "uuid-1",
        "events": [
          {
            "type": "start",
            "timestamp": "2024-01-01T09:00:00.000Z"
          },
          {
            "type": "pause",
            "timestamp": "2024-01-01T09:30:00.000Z"
          },
          {
            "type": "resume",
            "timestamp": "2024-01-01T09:45:00.000Z"
          },
          {
            "type": "end",
            "timestamp": "2024-01-01T10:30:00.000Z"
          }
        ]
      }
    ]
  }
}
```

### Page Tracking Endpoints

#### Track Page Visit
**POST** `/api/pages/track`

Tracks a page visit and time spent on the page.

**Authentication Required**: No

**Request Body**:
```json
{
  "user": "username",
  "page": "/dashboard",
  "timespent": 120,
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Page visit tracked successfully",
  "data": {
    "page": "/dashboard",
    "time_spent": 120,
    "timestamp": "2024-01-01T12:00:00.000Z"
  }
}
```

#### Get Page Statistics
**POST** `/api/pages/stats`

Retrieves page statistics including visit counts and average time spent.

**Authentication Required**: Yes

**Request Body**:
```json
{
  "app": "your_app_name",
  "user": "username"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "page_stats": {
      "/dashboard": {
        "visits": 45,
        "total_time": "02:15:30",
        "average_time": "00:03:00"
      },
      "/profile": {
        "visits": 20,
        "total_time": "01:30:00",
        "average_time": "00:04:30"
      }
    }
  }
}
```

### Health Check Endpoints

#### Root Health Check
**POST** `/`

Basic health check for the entire service.

**Authentication Required**: No

**Request Body**:
```json
{
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Session Server is running",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### API Health Check
**POST** `/api/health`

Health check specifically for the API service.

**Authentication Required**: No

**Request Body**:
```json
{
  "app": "your_app_name"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "API is healthy",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Usage Examples

### Starting a Session

```bash
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "john_doe",
    "time": "2024-01-01T12:00:00.000Z",
    "status": "active",
    "app": "my_app"
  }'
```

### Getting Session Analytics

```bash
curl -X POST http://localhost:8000/api/sessions/heatmap \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "my_app",
    "user": "john_doe"
  }'
```

### Tracking Page Visits

```bash
curl -X POST http://localhost:8000/api/pages/track \
  -H "Content-Type: application/json" \
  -d '{
    "user": "john_doe",
    "page": "/dashboard",
    "timespent": 120,
    "app": "my_app"
  }'
```

## Notes

- All timestamps should be in ISO 8601 format with timezone information
- Session IDs are UUIDs generated by the server
- Time durations are returned in HH:MM:SS format
- Page paths should include the leading slash
- User parameter can be set to "all" for aggregate data in analytics endpoints 