from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import connect_to_mongo
from app.api.routes import auth_router, session_router, page_router
from app.models.models import AppRequest
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield

app = FastAPI(
    title="Session and Page Tracking API",
    description="Backend API for tracking user sessions and page visits",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        "http://unfogg.cerebralzip.com",
        "https://unfogg.cerebralzip.com",
        "http://discoveryqaz.cerebralzip.com",
        "https://discoveryqaz.cerebralzip.com",
        "http://0.0.0.0:3000/",
        "http://0.0.0.0:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(page_router, prefix="/api/pages", tags=["Page Tracking"])
app.include_router(session_router, prefix="/api/sessions", tags=["Session Tracking"])

@app.post("/")
async def root(app_data: AppRequest):
    return {"message": "Session and Page Tracking API is running!", "app": app_data.app}

@app.post("/api/health")
async def health_check(app_data: AppRequest):
    return {
        "status": "success",
        "message": "Server is running",
        "timestamp": datetime.utcnow().isoformat(),
        "app": app_data.app
    } 