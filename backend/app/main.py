"""
FastAPI application for IntelliGrid backend.
"""
import sys
import os

# Add src to path BEFORE any other imports
# backend/app/main.py -> backend/ -> backend/src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import simulation, optimization, weather, impact
from app.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("🚀 IntelliGrid API starting up...")
    yield
    logger.info("👋 IntelliGrid API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="IntelliGrid API",
    description="Smart Home Energy Management System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "https://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(simulation.router, prefix="/api/v1", tags=["simulation"])
app.include_router(optimization.router, prefix="/api/v1", tags=["optimization"])
app.include_router(weather.router, prefix="/api/v1", tags=["weather"])
app.include_router(impact.router, prefix="/api/v1", tags=["impact"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "IntelliGrid API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "simulate": "/api/v1/simulate",
            "optimize": "/api/v1/optimize",
            "compare": "/api/v1/compare",
            "weather_alerts": "/api/v1/weather/alerts",
            "impact": "/api/v1/impact"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "IntelliGrid API"}
