# app/main_minimal.py
"""
Minimal starter version of the main.py file.
This can be used to verify the basic FastAPI setup works
without requiring all the modules to be implemented.
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import logging

# Initialize FastAPI app
app = FastAPI(
    title="IIT Chicago AI Enrollment Assistant",
    description="Voice-activated system for enrollment counselors to manage student communications through Slate CRM",
    version="0.1.0-minimal"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy", "version": app.version}

# Root endpoint with basic info
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint with basic application information"""
    return {
        "application": "IIT Chicago AI Enrollment Assistant",
        "status": "online",
        "api_docs": "/docs",
        "version": app.version,
        "mode": "minimal starter"
    }

# Run on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Enrollment Assistant API (minimal version)")

# Run on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Enrollment Assistant API")