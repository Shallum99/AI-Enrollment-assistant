# tests/core/test_workflow_controller.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock
import uuid

from app.core.workflow_controller import WorkflowController, WorkflowState, WorkflowSession

# Fixture for a workflow controller
@pytest.fixture
async def workflow_controller():
    controller = WorkflowController()
    
    # Mock the voice activator to avoid real initialization
    with patch('app.utils.voice_activation.initialize_voice_activator') as mock_init:
        mock_activator = MagicMock()
        mock_init.return_value = mock_activator
        
        await controller.initialize()
        
        yield controller

# Test session creation
@pytest.mark.asyncio
async def test_create_session(workflow_controller):
    result = await workflow_controller.create_session()
    
    assert result["status"] == "created"
    assert "session_id" in result
    assert result["session_id"] in workflow_controller.sessions
    
    session = workflow_controller.sessions[result["session_id"]]
    assert session.current_state == WorkflowState.LISTENING
    assert len(session.events) == 1

# Test end session
@pytest.mark.asyncio
async def test_end_session(workflow_controller):
    # Create a session first
    create_result = await workflow_controller.create_session()
    session_id = create_result["session_id"]
    
    # End the session
    end_result = await workflow_controller.end_session(session_id)
    
    assert end_result["status"] == "ended"
    assert end_result["session_id"] == session_id
    assert session_id not in workflow_controller.sessions

# Test nonexistent session
@pytest.mark.asyncio
async def test_end_nonexistent_session(workflow_controller):
    # Try to end a session that doesn't exist
    fake_session_id = str(uuid.uuid4())
    result = await workflow_controller.end_session(fake_session_id)
    
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()

# Test get session
@pytest.mark.asyncio
async def test_get_session(workflow_controller):
    # Create a session first
    create_result = await workflow_controller.create_session()
    session_id = create_result["session_id"]
    
    # Get the session info
    session_info = await workflow_controller.get_session(session_id)
    
    assert session_info["session_id"] == session_id
    assert session_info["current_state"] == WorkflowState.LISTENING
    assert session_info["browser_session_id"] is None
    assert session_info["current_email_id"] is None
    assert session_info["has_draft"] is False
    assert "start_time" in session_info
    assert session_info["events"] == 1

# Test get all sessions
@pytest.mark.asyncio
async def test_get_all_sessions(workflow_controller):
    # Create a couple of sessions
    await workflow_controller.create_session()
    await workflow_controller.create_session()
    
    # Get all sessions
    sessions = await workflow_controller.get_all_sessions()
    
    assert len(sessions) == 2
    assert all("session_id" in session for session in sessions)
    assert all("current_state" in session for session in sessions)

# Test process voice command
@pytest.mark.asyncio
async def test_process_voice_command(workflow_controller):
    # Test with an unknown command
    with patch.object(workflow_controller, '_process_command') as mock_process:
        mock_process.return_value = {
            "status": "error",
            "message": "Unknown command"
        }
        
        result = await workflow_controller.process_voice_command("test command")
        
        assert result["status"] == "error"
        assert result["message"] == "Unknown command"
        assert len(workflow_controller.sessions) == 1  # Should create a session

# Test command processing with mocked handlers
@pytest.mark.asyncio
async def test_login_command(workflow_controller):
    # Create a session
    create_result = await workflow_controller.create_session()
    session_id = create_result["session_id"]
    session = workflow_controller.sessions[session_id]
    
    # Mock the login handler
    with patch.object(workflow_controller, '_handle_login_command') as mock_login:
        mock_login.return_value = {
            "status": "success",
            "message": "Authentication successful"
        }
        
        # Mock the process command to call our handler directly
        with patch.object(workflow_controller, '_process_command', wraps=workflow_controller._process_command) as mock_process:
            result = await workflow_controller.process_voice_command("login to Slate")
            
            assert result["status"] == "success"
            assert result["message"] == "Authentication successful"
            mock_login.assert_called_once()

# Test event listener registration
@pytest.mark.asyncio
async def test_event_listener(workflow_controller):
    # Create a mock event listener
    mock_listener = MagicMock()
    
    # Register the listener
    workflow_controller.register_event_listener(mock_listener)
    
    # Create a session which should trigger a notification
    await workflow_controller.create_session()
    
    # Verify the listener was called
    assert mock_listener.called
    assert mock_listener.call_count == 1
    
    # Get the event that was passed to the listener
    event = mock_listener.call_args[0][0]
    assert event.state == WorkflowState.LISTENING