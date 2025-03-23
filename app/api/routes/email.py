# app/api/routes/email.py
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

# Import our email services (to be implemented)
from app.services.email import email_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Models
class EmailRequest(BaseModel):
    """Email processing request model"""
    session_id: str
    email_id: Optional[str] = None  # If None, process first email in inbox
    
class EmailContent(BaseModel):
    """Email content model"""
    email_id: str
    subject: str
    sender: str
    recipient: str
    date: str
    body: str
    attachments: Optional[List[str]] = None
    
class EmailResponse(BaseModel):
    """Response model for email processing"""
    email: EmailContent
    suggested_response: str
    intent: str
    confidence: float
    
class DraftResponse(BaseModel):
    """Request model for submitting a draft response"""
    email_id: str
    session_id: str
    response_text: str
    send: bool = False  # Whether to send or just save as draft

# Routes
@router.post("/process", response_model=EmailResponse)
async def process_email(request: EmailRequest):
    """Process an email and generate a suggested response"""
    try:
        logger.info(f"Processing email for session: {request.session_id}")
        result = await email_service.process_email(
            session_id=request.session_id,
            email_id=request.email_id
        )
        return result
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing email: {str(e)}"
        )

@router.post("/draft", response_model=Dict[str, Any])
async def submit_email_draft(request: DraftResponse):
    """Submit a draft email response"""
    try:
        result = await email_service.submit_draft(
            email_id=request.email_id,
            session_id=request.session_id,
            response_text=request.response_text,
            send=request.send
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error submitting email draft: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting email draft: {str(e)}"
        )

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_emails(session_id: str, limit: int = 10):
    """List emails in the inbox"""
    try:
        emails = await email_service.list_emails(
            session_id=session_id,
            limit=limit
        )
        return emails
    except Exception as e:
        logger.error(f"Error listing emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing emails: {str(e)}"
        )