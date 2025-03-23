# app/main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

# Import our modules
from app.core.config import settings
from app.api.routes import api_router
from app.core.logging import setup_logging
from app.core.workflow_controller import workflow_controller
from app.core.monitoring import service_monitor

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="IIT Chicago AI Enrollment Assistant",
    description="Voice-activated system for enrollment counselors to manage student communications through Slate CRM",
    version="0.1.0"
)

# Create static directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy", "version": app.version}

# Monitoring endpoints
@app.get("/metrics", status_code=status.HTTP_200_OK)
async def get_metrics():
    """Get system and service metrics"""
    system_metrics = service_monitor.get_system_metrics()
    service_metrics = service_monitor.get_all_metrics()
    
    return {
        "system": system_metrics,
        "services": service_metrics
    }

@app.get("/metrics/{service_name}", status_code=status.HTTP_200_OK)
async def get_service_metrics(service_name: str):
    """Get metrics for a specific service"""
    metrics = service_monitor.get_service_metrics(service_name)
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service_name} not found"
        )
    
    return metrics.to_dict()

# Root endpoint with basic info
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Serve the frontend UI"""
    # Check if index.html exists in static directory
    index_path = static_dir / "index.html"
    
    if index_path.exists():
        return FileResponse(index_path)
    else:
        # Fallback to API info if frontend not found
        return {
            "application": "IIT Chicago AI Enrollment Assistant",
            "status": "online",
            "api_docs": "/docs",
            "version": app.version,
            "note": "Frontend UI not found. Create static/index.html to enable UI."
        }

# Workflow controller endpoints
@app.post("/workflow/command")
async def process_command(command: str):
    """Process a voice command directly (without voice recognition)"""
    return await workflow_controller.process_voice_command(command)

@app.get("/workflow/sessions")
async def get_all_sessions():
    """Get all active workflow sessions"""
    return await workflow_controller.get_all_sessions()

@app.get("/workflow/session/{session_id}")
async def get_session(session_id: str):
    """Get information about a specific workflow session"""
    session = await workflow_controller.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return session

@app.post("/workflow/session/{session_id}/end")
async def end_session(session_id: str):
    """End a workflow session"""
    return await workflow_controller.end_session(session_id)

# Run on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Enrollment Assistant API")
    
    # Start monitoring background task
    asyncio.create_task(service_monitor.monitor_task(interval_seconds=300))
    logger.info("Service monitoring task started")
    
    # Initialize workflow controller
    try:
        await workflow_controller.initialize()
        logger.info("Workflow controller initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing workflow controller: {str(e)}")
        # Continue startup even if workflow controller fails
        # This allows API to run for diagnostics

# Run on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Enrollment Assistant API")
    # Clean up resources