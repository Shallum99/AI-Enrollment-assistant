# app/core/workflow_controller.py
import logging
import asyncio
import os
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

# Import our services
from app.services.browser import browser_service
from app.services.email import email_service
from app.services.voice import voice_service
from app.utils.voice_activation import initialize_voice_activator
from app.core.config import settings

logger = logging.getLogger(__name__)

class WorkflowState(str, Enum):
    """Enum representing the current state of the workflow"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING_COMMAND = "processing_command"
    AUTHENTICATING = "authenticating"
    NAVIGATING = "navigating"
    READING_EMAIL = "reading_email"
    GENERATING_RESPONSE = "generating_response"
    REVIEWING = "reviewing"
    SUBMITTING = "submitting"
    ERROR = "error"

class WorkflowEvent(BaseModel):
    """Model for workflow events"""
    state: WorkflowState
    timestamp: datetime = datetime.now()
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

@dataclass
class WorkflowSession:
    """Data class for a workflow session"""
    session_id: str
    browser_session_id: Optional[str] = None
    current_email_id: Optional[str] = None
    current_state: WorkflowState = WorkflowState.IDLE
    draft_response: Optional[str] = None
    start_time: datetime = datetime.now()
    events: List[WorkflowEvent] = None
    
    def __post_init__(self):
        """Initialize events list if None"""
        if self.events is None:
            self.events = []
    
    def add_event(self, state: WorkflowState, data: Optional[Dict[str, Any]] = None, message: Optional[str] = None):
        """Add an event to the session history"""
        event = WorkflowEvent(state=state, data=data, message=message)
        self.events.append(event)
        self.current_state = state
        return event

class WorkflowController:
    """Controller for orchestrating the entire email processing workflow"""
    
    def __init__(self):
        """Initialize the workflow controller"""
        self.sessions = {}  # Dict of active sessions
        self.voice_activator = None
        self.event_listeners = []  # Callbacks for state changes
    
    async def initialize(self):
        """Initialize the workflow controller"""
        logger.info("Initializing workflow controller")
        
        # Initialize voice activation with a callback to our command handler
        self.voice_activator = await initialize_voice_activator(
            wake_word=settings.WAKE_WORD,
            callback=self._handle_voice_event
        )
        
        logger.info("Workflow controller initialized successfully")
        return {"status": "initialized"}
    
    async def _handle_voice_event(self, event: Dict[str, Any]):
        """Handle voice events from the voice activator"""
        logger.info(f"Received voice event: {event}")
        
        event_type = event.get("event")
        
        if event_type == "wake_word_detected":
            # Create a new session when wake word is detected
            await self.create_session()
        
        elif event_type == "command_detected":
            # Process the detected command
            command = event.get("command")
            active_session = self._get_active_session()
            
            if active_session:
                await self._process_command(active_session, command)
            else:
                logger.warning("Received command but no active session exists")
    
    async def create_session(self) -> Dict[str, Any]:
        """Create a new workflow session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        session = WorkflowSession(session_id=session_id)
        session.add_event(
            state=WorkflowState.LISTENING,
            message="Session created, listening for commands"
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new workflow session: {session_id}")
        
        # Notify listeners
        await self._notify_listeners(session.events[-1])
        
        return {"session_id": session_id, "status": "created"}
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a workflow session"""
        if session_id not in self.sessions:
            logger.warning(f"Attempted to end non-existent session: {session_id}")
            return {"status": "error", "message": "Session not found"}
        
        session = self.sessions[session_id]
        
        # Close browser session if active
        if session.browser_session_id:
            try:
                await browser_service.manage_session(
                    action="end",
                    session_id=session.browser_session_id
                )
            except Exception as e:
                logger.error(f"Error closing browser session: {str(e)}")
        
        # Add final event and remove from active sessions
        session.add_event(
            state=WorkflowState.IDLE,
            message="Session ended"
        )
        
        # Notify listeners
        await self._notify_listeners(session.events[-1])
        
        # Remove from active sessions
        del self.sessions[session_id]
        
        logger.info(f"Ended workflow session: {session_id}")
        return {"status": "ended", "session_id": session_id}
    
    async def _process_command(self, session: WorkflowSession, command: str) -> Dict[str, Any]:
        """Process a voice command"""
        logger.info(f"Processing command for session {session.session_id}: {command}")
        
        # Update session state
        session.add_event(
            state=WorkflowState.PROCESSING_COMMAND,
            data={"command": command},
            message=f"Processing command: {command}"
        )
        
        # Notify listeners
        await self._notify_listeners(session.events[-1])
        
        # Handle different commands
        # This is a simplified implementation - in a real system, you would use
        # more sophisticated NLU to understand commands
        command_lower = command.lower()
        
        try:
            if "login" in command_lower or "log in" in command_lower:
                return await self._handle_login_command(session)
            
            elif "inbox" in command_lower or "emails" in command_lower:
                return await self._handle_inbox_command(session)
            
            elif "read" in command_lower and ("email" in command_lower or "message" in command_lower):
                return await self._handle_read_email_command(session)
            
            elif "generate" in command_lower or "respond" in command_lower or "reply" in command_lower:
                return await self._handle_generate_response_command(session)
            
            elif "submit" in command_lower or "send" in command_lower:
                return await self._handle_submit_response_command(session, send=True)
            
            elif "save" in command_lower and "draft" in command_lower:
                return await self._handle_submit_response_command(session, send=False)
            
            else:
                # Unknown command
                logger.warning(f"Unknown command: {command}")
                session.add_event(
                    state=WorkflowState.ERROR,
                    message=f"Unknown command: {command}"
                )
                await self._notify_listeners(session.events[-1])
                return {"status": "error", "message": "Unknown command"}
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            session.add_event(
                state=WorkflowState.ERROR,
                message=f"Error processing command: {str(e)}"
            )
            await self._notify_listeners(session.events[-1])
            return {"status": "error", "message": str(e)}
    
    async def _handle_login_command(self, session: WorkflowSession) -> Dict[str, Any]:
        """Handle login command"""
        logger.info(f"Handling login command for session {session.session_id}")
        
        # Update session state
        session.add_event(
            state=WorkflowState.AUTHENTICATING,
            message="Authenticating to Slate CRM"
        )
        await self._notify_listeners(session.events[-1])
        
        try:
            # Authenticate to CRM
            result = await browser_service.login_to_crm(
                username=settings.SLATE_USERNAME,
                password=settings.SLATE_PASSWORD,
                security_answer="tanki online"  # From your requirements
            )
            
            if result["status"] == "success":
                # Store browser session ID
                session.browser_session_id = result["session_id"]
                
                session.add_event(
                    state=WorkflowState.LISTENING,
                    message="Authentication successful, listening for next command"
                )
                await self._notify_listeners(session.events[-1])
                
                return {"status": "success", "message": "Authentication successful"}
            else:
                # Authentication failed
                session.add_event(
                    state=WorkflowState.ERROR,
                    message=f"Authentication failed: {result.get('error')}"
                )
                await self._notify_listeners(session.events[-1])
                
                return {"status": "error", "message": "Authentication failed"}
                
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            session.add_event(
                state=WorkflowState.ERROR,
                message=f"Error during authentication: {str(e)}"
            )
            await self._notify_listeners(session.events[-1])
            
            return {"status": "error", "message": str(e)}
    
    async def _handle_inbox_command(self, session: WorkflowSession) -> Dict[str, Any]:
        """Handle inbox navigation command"""
        logger.info(f"Handling inbox command for session {session.session_id}")
        
        if not session.browser_session_id:
            logger.warning("Cannot navigate to inbox: Not authenticated")
            session.add_event(
                state=WorkflowState.ERROR,
                message="Cannot navigate to inbox: Not authenticated"
            )
            await self._notify_listeners(session.events[-1])
            return {"status": "error", "message": "Not authenticated"}
        
        # Update session state
        session.add_event(
            state=WorkflowState.NAVIGATING,
            message="Navigating to inbox"
        )
        await self._notify_listeners(session.events[-1])
        
        try:
            # Navigate to inbox
            result = await browser_service.navigate_to_inbox(
                session_id=session.browser_session_id
            )
            
            if result["status"] == "success":
                session.add_event(
                    state=WorkflowState.LISTENING,
                    message="Navigation successful, listening for next command"
                )
                await self._notify_listeners(session.events[-1])
                
                return {"status": "success", "message": "Navigation successful"}
            else:
                # Navigation failed
                session.add_event(
                    state=WorkflowState.ERROR,
                    message=f"Navigation failed: {result.get('error')}"
                )
                await self._notify_listeners(session.events[-1])
                
                return {"status": "error", "message": "Navigation failed"}
                
        except Exception as e:
            logger.error(f"Error during navigation: {str(e)}")
            session.add_event(
                state=WorkflowState.ERROR,
                message=f"Error during navigation: {str(e)}"
            )
            await self._notify_listeners(session.events[-1])
            
            return {"status": "error", "message": str(e)}
    
    async def _handle_read_email_command(self, session: WorkflowSession) -> Dict[str, Any]:
        """Handle read email command"""
        logger.info(f"Handling read email command for session {session.session_id}")
        
        if not session.browser_session_id:
            logger.warning("Cannot read email: Not authenticated")
            session.add_event(
                state=WorkflowState.ERROR,
                message="Cannot read email: Not authenticated"
            )
            await self._notify_listeners(session.events[-1])
            return {"status": "error", "message": "Not authenticated"}
        
        # Update session state
        session.add_event(
            state=WorkflowState.READING_EMAIL,
            message="Reading email"
        )
        await self._notify_listeners(session.events[-1])
        
        try:
            # Process email using email service
            result = await email_service.process_email(
                session_id=session.browser_session_id,
                email_id=None  # Process first email in inbox
            )
            
            # Store email ID for later use
            session.current_email_id = result["email"]["email_id"]
            
            session.add_event(
                state=WorkflowState.LISTENING,
                data={"email": result["email"]},
                message=f"Email read: {result['email']['subject']}"
            )
            await self._notify_listeners(session.events[-1])
            
            return {
                "status": "success", 
                "message": "Email read successfully",
                "email": result["email"]
            }
                
        except Exception as e:
            logger.error(f"Error reading email: {str(e)}")
            session.add_event(
                state=WorkflowState.ERROR,
                message=f"Error reading email: {str(e)}"
            )
            await self._notify_listeners(session.events[-1])
            
            return {"status": "error", "message": str(e)}
    
    async def _handle_generate_response_command(self, session: WorkflowSession) -> Dict[str, Any]:
        """Handle generate response command"""
        logger.info(f"Handling generate response command for session {session.session_id}")
        
        if not session.current_email_id:
            logger.warning("Cannot generate response: No email selected")
            session.add_event(
                state=WorkflowState.ERROR,
                message="Cannot generate response: No email selected"
            )
            await self._notify_listeners(session.events[-1])
            return {"status": "error", "message": "No email selected"}
        
        # Update session state
        session.add_event(
            state=WorkflowState.GENERATING_RESPONSE,
            message="Generating email response"
        )
        await self._notify_listeners(session.events[-1])
        
        try:
            # Process email to get suggested response
            result = await email_service.process_email(
                session_id=session.browser_session_id,
                email_id=session.current_email_id
            )
            
            # Store suggested response
            session.draft_response = result["suggested_response"]
            
            session.add_event(
                state=WorkflowState.REVIEWING,
                data={"draft_response": session.draft_response},
                message="Response generated, ready for review"
            )
            await self._notify_listeners(session.events[-1])
            
            return {
                "status": "success", 
                "message": "Response generated",
                "draft_response": session.draft_response
            }
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            session.add_event(
                state=WorkflowState.ERROR,
                message=f"Error generating response: {str(e)}"
            )
            await self._notify_listeners(session.events[-1])
            
            return {"status": "error", "message": str(e)}
    
    async def _handle_submit_response_command(self, session: WorkflowSession, send: bool) -> Dict[str, Any]:
        """Handle submit response command"""
        logger.info(f"Handling submit response command for session {session.session_id}, send={send}")
        
        if not session.current_email_id:
            logger.warning("Cannot submit response: No email selected")
            session.add_event(
                state=WorkflowState.ERROR,
                message="Cannot submit response: No email selected"
            )
            await self._notify_listeners(session.events[-1])
            return {"status": "error", "message": "No email selected"}
        
        if not session.draft_response:
            logger.warning("Cannot submit response: No draft response created")
            session.add_event(
                state=WorkflowState.ERROR,
                message="Cannot submit response: No draft response created"
            )
            await self._notify_listeners(session.events[-1])
            return {"status": "error", "message": "No draft response created"}
        
        # Update session state
        session.add_event(
            state=WorkflowState.SUBMITTING,
            message=f"Submitting response as {'email' if send else 'draft'}"
        )
        await self._notify_listeners(session.events[-1])
        
        try:
            # Submit draft response
            result = await email_service.submit_draft(
                email_id=session.current_email_id,
                session_id=session.browser_session_id,
                response_text=session.draft_response,
                send=send
            )
            
            action = "sent" if send else "saved as draft"
            
            session.add_event(
                state=WorkflowState.LISTENING,
                message=f"Response {action} successfully"
            )
            await self._notify_listeners(session.events[-1])
            
            # Clear current email and draft
            session.current_email_id = None
            session.draft_response = None
            
            return {
                "status": "success", 
                "message": f"Response {action} successfully"
            }
                
        except Exception as e:
            logger.error(f"Error submitting response: {str(e)}")
            session.add_event(
                state=WorkflowState.ERROR,
                message=f"Error submitting response: {str(e)}"
            )
            await self._notify_listeners(session.events[-1])
            
            return {"status": "error", "message": str(e)}
    
    def _get_active_session(self) -> Optional[WorkflowSession]:
        """Get the most recently active session, if any"""
        if not self.sessions:
            return None
        
        # Find most recent session that isn't in IDLE state
        active_sessions = [s for s in self.sessions.values() if s.current_state != WorkflowState.IDLE]
        if not active_sessions:
            return None
        
        # Sort by most recent start time
        return sorted(active_sessions, key=lambda s: s.start_time, reverse=True)[0]
    
    def register_event_listener(self, callback: Callable[[WorkflowEvent], None]):
        """Register a callback for workflow events"""
        self.event_listeners.append(callback)
        logger.info(f"Registered new event listener, total: {len(self.event_listeners)}")
    
    async def _notify_listeners(self, event: WorkflowEvent):
        """Notify all registered listeners of a state change"""
        for listener in self.event_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event)
                else:
                    listener(event)
            except Exception as e:
                logger.error(f"Error in event listener: {str(e)}")
    
    async def process_voice_command(self, command: str) -> Dict[str, Any]:
        """Process a voice command programmatically (not from voice activator)"""
        active_session = self._get_active_session()
        
        if not active_session:
            # Create a new session
            result = await self.create_session()
            active_session = self.sessions[result["session_id"]]
        
        # Process the command
        return await self._process_command(active_session, command)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session.session_id,
            "browser_session_id": session.browser_session_id,
            "current_state": session.current_state,
            "current_email_id": session.current_email_id,
            "has_draft": bool(session.draft_response),
            "start_time": session.start_time.isoformat(),
            "events": len(session.events),
            "last_event": session.events[-1].dict() if session.events else None
        }
    
    async def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all sessions"""
        return [await self.get_session(session_id) for session_id in self.sessions]

# Initialize controller
workflow_controller = WorkflowController()