from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    dashboard,
    words,
    groups,
    study_activities,
    study_sessions,
    system
)
from .utils import PaginationParams  # Import from utils, not models
from .database import models  # Add this import

app = FastAPI(
    title="Language Learning Portal API",
    description="API for managing vocabulary and study sessions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(dashboard.router)
app.include_router(words.router)
app.include_router(groups.router)
app.include_router(study_activities.router)
app.include_router(study_sessions.router)
app.include_router(system.router)

@app.get("/")
async def root():
    """Root endpoint returning API info"""
    return {
        "name": "Language Learning Portal API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 