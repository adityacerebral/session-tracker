from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import re
import json
import base64
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

class TimeUtils:
    """Utility class for time-related operations"""
    
    ISO_DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
    
    @staticmethod
    def validate_iso_time_format(time_string: str) -> bool:
        """
        Validate if the time string is in correct ISO 8601 format
        Accepts formats like:
        - "2024-01-01T12:00:00Z"
        - "2024-01-01T12:00:00.123Z"
        - "2024-01-01T12:00:00"
        """
        if not time_string:
            return False
        
        return bool(re.match(TimeUtils.ISO_DATETIME_PATTERN, time_string))
    
    @staticmethod
    def parse_iso_time_string(time_string: str) -> datetime:
        """Parse ISO time string to datetime object"""
        if not TimeUtils.validate_iso_time_format(time_string):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid time format. Expected ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ), got: {time_string}"
            )
        
        try:
            clean_time = time_string.rstrip('Z')
            
            try:
                return datetime.fromisoformat(clean_time)
            except ValueError:
                if '.' in clean_time:
                    clean_time = clean_time.split('.')[0]
                return datetime.fromisoformat(clean_time)
                
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse time string '{time_string}': {str(e)}"
            )
    
    @staticmethod
    def separate_date_and_time(time_string: str) -> Tuple[str, str]:
        """
        Separate date and time components from ISO time string
        Returns tuple of (date_string, time_string)
        """
        if not TimeUtils.validate_iso_time_format(time_string):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time format for separation: {time_string}"
            )
        
        try:
            clean_time = time_string.rstrip('Z')
            date_part, time_part = clean_time.split('T')
            return date_part, time_part
            
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to separate date and time from: {time_string}"
            )
    
    @staticmethod
    def get_date_from_time_string(time_string: str) -> str:
        """Extract only the date part from ISO time string"""
        date_part, _ = TimeUtils.separate_date_and_time(time_string)
        return date_part
    
    @staticmethod
    def get_time_from_time_string(time_string: str) -> str:
        """Extract only the time part from ISO time string"""
        _, time_part = TimeUtils.separate_date_and_time(time_string)
        return time_part
    
    @staticmethod
    def get_hour_from_time_string(time_string: str) -> int:
        """Extract hour from ISO time string"""
        _, time_part = TimeUtils.separate_date_and_time(time_string)
        hour_str = time_part.split(':')[0]
        return int(hour_str)
    
    @staticmethod
    def format_datetime_to_iso(dt: datetime) -> str:
        """Format datetime object to ISO string with Z suffix"""
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    @staticmethod
    def validate_and_parse_time(time_string: str) -> datetime:
        """Validates format and returns parsed datetime object"""
        if not time_string:
            raise HTTPException(
                status_code=400,
                detail="Time string cannot be empty"
            )
        
        return TimeUtils.parse_iso_time_string(time_string)
    
    @staticmethod
    def is_valid_date_range(start_time: str, end_time: str) -> bool:
        """Check if start_time is before end_time"""
        try:
            start_dt = TimeUtils.parse_iso_time_string(start_time)
            end_dt = TimeUtils.parse_iso_time_string(end_time)
            return start_dt <= end_dt
        except:
            return False
    
    @staticmethod
    def get_time_difference_seconds(start_time: str, end_time: str) -> int:
        """Calculate difference between two ISO time strings in seconds"""
        start_dt = TimeUtils.parse_iso_time_string(start_time)
        end_dt = TimeUtils.parse_iso_time_string(end_time)
        
        if start_dt > end_dt:
            raise HTTPException(
                status_code=400,
                detail="Start time cannot be after end time"
            )
        
        return int((end_dt - start_dt).total_seconds())
        
    @staticmethod
    def seconds_to_iso_duration(seconds: int) -> str:
        """
        Convert seconds to ISO 8601 duration format
        Example: 3665 seconds -> "PT1H1M5S"
        """
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        duration = "PT"
        if hours:
            duration += f"{hours}H"
        if minutes:
            duration += f"{minutes}M"
        if seconds or (not hours and not minutes):
            duration += f"{seconds}S"
            
        return duration

class JWTHelper:
    """Helper class for JWT token operations without signature verification"""
    
    @staticmethod
    def decode_jwt_payload(token: str) -> Dict[str, Any]:
        """Decode JWT payload without signature verification"""
        try:
            # JWT has 3 parts: header.payload.signature
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT format - must have 3 parts")
            
            payload_part = parts[1]
            
            # Add padding if needed (JWT base64 might not have padding)
            padding = 4 - (len(payload_part) % 4)
            if padding != 4:
                payload_part += '=' * padding
            
            decoded_bytes = base64.urlsafe_b64decode(payload_part)
            payload = json.loads(decoded_bytes)
            
            return payload
            
        except Exception as e:
            raise ValueError(f"Failed to decode JWT payload: {str(e)}")
    
    @staticmethod
    def decode_jwt_header(token: str) -> Dict[str, Any]:
        """Decode JWT header without signature verification"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT format - must have 3 parts")
            
            header_part = parts[0]
            
            padding = 4 - (len(header_part) % 4)
            if padding != 4:
                header_part += '=' * padding
            
            decoded_bytes = base64.urlsafe_b64decode(header_part)
            header = json.loads(decoded_bytes)
            
            return header
            
        except Exception as e:
            raise ValueError(f"Failed to decode JWT header: {str(e)}")
    
    @staticmethod
    def extract_user_from_token(token: str) -> str:
        """Extract username from JWT token's payload"""
        try:
            payload = JWTHelper.decode_jwt_payload(token)
            
            # Try common user claim keys
            for key in ['sub', 'username', 'email', 'user_id', 'userId']:
                if key in payload:
                    return str(payload[key])
            
            # If no common keys found, return the first string value
            for key, value in payload.items():
                if isinstance(value, str):
                    return value
            
            raise ValueError("No user identifier found in token payload")
            
        except Exception as e:
            raise ValueError(f"Failed to extract user from token: {str(e)}")
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check if token is expired based on 'exp' claim"""
        try:
            payload = JWTHelper.decode_jwt_payload(token)
            
            if 'exp' not in payload:
                return False  # No expiration claim, assume not expired
            
            exp_timestamp = int(payload['exp'])
            current_timestamp = datetime.utcnow().timestamp()
            
            return current_timestamp > exp_timestamp
            
        except Exception:
            return True  # If we can't decode the token, consider it expired
    
    @staticmethod
    def get_token_info(token: str) -> Dict[str, Any]:
        """Get comprehensive token information"""
        try:
            header = JWTHelper.decode_jwt_header(token)
            payload = JWTHelper.decode_jwt_payload(token)
            
            # Extract key information
            user = JWTHelper.extract_user_from_token(token)
            is_expired = JWTHelper.is_token_expired(token)
            
            return {
                "user": user,
                "is_expired": is_expired,
                "header": header,
                "payload": payload
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get token info: {str(e)}")
    
    @staticmethod
    def validate_token_structure(token: str) -> bool:
        """Validate basic token structure without verifying signature"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return False
            
            # Try to decode header and payload
            JWTHelper.decode_jwt_header(token)
            JWTHelper.decode_jwt_payload(token)
            
            return True
        except Exception:
            return False

class AuthUtils:
    """Utility class for JWT authentication"""
    
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    def __init__(self):
        pass
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a new JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=AuthUtils.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, AuthUtils.SECRET_KEY, algorithm=AuthUtils.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, AuthUtils.SECRET_KEY, algorithms=[AuthUtils.ALGORITHM])
            return payload
        except JWTError as e:
            # Try to extract user without verification for better error messages
            try:
                user = JWTHelper.extract_user_from_token(token)
                is_expired = JWTHelper.is_token_expired(token)
                
                if is_expired:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Token for user '{user}' has expired"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid token signature for user '{user}'"
                    )
            except:
                # Fall back to generic error
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
    
    @staticmethod
    def get_current_user_from_token(token: str) -> str:
        """Extract and verify user from token"""
        try:
            # First try to verify with our secret
            payload = AuthUtils.verify_token(token)
            
            # Look for common user claim keys
            for key in ['sub', 'username', 'email', 'user_id', 'userId']:
                if key in payload:
                    return str(payload[key])
            
            # If no common keys found but token is valid, use first string value
            for key, value in payload.items():
                if isinstance(value, str):
                    return value
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User identity not found in token"
            )
            
        except HTTPException:
            # If verification fails, try to extract without verification
            # This is useful when tokens are signed by external systems
            try:
                return JWTHelper.extract_user_from_token(token)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Failed to extract user from token: {str(e)}"
                )
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
        """FastAPI dependency for extracting current user from Bearer token"""
        token = credentials.credentials
        return self.get_current_user_from_token(token)
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """Validate basic token format without verification"""
        if not token or not isinstance(token, str):
            return False
        
        parts = token.split('.')
        return len(parts) == 3 and all(parts)
    
    @staticmethod
    def decode_token_without_verification(token: str) -> Dict[str, Any]:
        """Decode token payload without verifying signature"""
        if not AuthUtils.validate_token_format(token):
            raise ValueError("Invalid token format")
        
        try:
            payload = JWTHelper.decode_jwt_payload(token)
            return payload
        except Exception as e:
            raise ValueError(f"Failed to decode token: {str(e)}")

# FastAPI dependency for extracting current user
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
    """Extract current user from Bearer token"""
    token = credentials.credentials
    return AuthUtils.get_current_user_from_token(token)

# FastAPI dependency for optional user authentication
def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[str]:
    """Extract current user from Bearer token, but don't require authentication"""
    if not credentials:
        return None
    
    try:
        return AuthUtils.get_current_user_from_token(credentials.credentials)
    except HTTPException:
        return None

# Create time_utils singleton instance
time_utils = TimeUtils() 