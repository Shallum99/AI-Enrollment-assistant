# app/api/routes/workflow.py
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

# Import our workflow controller
from app.core.workflow_controller import workflow_controller, WorkflowState

router = APIRouter()
logger = logging.getLogger(__name__)

# Models
class CommandRequest(BaseModel):
    """Request model for voice commands"""
    command: str
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    """Response model for workflow sessions"""
    session_id: str
    current_state: WorkflowState
    browser_session_id: Optional[str] = None
    current_email_id: Optional[str] = None
    has_draft: bool
    start_time: str
    events: int

# Routes
@router.post("/command", response_model=Dict[str, Any])
async def process_command(request: CommandRequest):
    """Process a voice command"""
    try:
        if request.session_id:
            # TODO: Implement command processing for specific session
            # For now, we'll just use the active session
            pass
        
        result = await workflow_controller.process_voice_command(request.command)
        return result
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing command: {str(e)}"
        )

@router.post("/session", response_model=Dict[str, Any])
async def create_session():
    """Create a new workflow session"""
    try:
        result = await workflow_controller.create_session()
        return result
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )

@router.delete("/session/{session_id}", response_model=Dict[str, Any])
async def end_session(session_id: str):
    """End a workflow session"""
    try:
        result = await workflow_controller.end_session(session_id)
        return result
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending session: {str(e)}"
        )

@router.get("/sessions", response_model=List[Dict[str, Any]])
async def get_all_sessions():
    """Get all active workflow sessions"""
    try:
        return await workflow_controller.get_all_sessions()
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sessions: {str(e)}"
        )

@router.get("/session/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    """Get information about a specific workflow session"""
    try:
        session = await workflow_controller.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting session: {str(e)}"
        )