# app/api/routes/__init__.py
from fastapi import APIRouter
from app.api.routes import voice, browser, email, workflow

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(browser.router, prefix="/browser", tags=["browser"])
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])