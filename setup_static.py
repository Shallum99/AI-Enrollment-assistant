#!/usr/bin/env python
"""
Script to set up static files for the IIT Chicago AI Enrollment Assistant.
This will create the static directory and save the index.html file.
"""
import os
import sys
from pathlib import Path

def setup_static_files():
    """Set up static files for the web UI"""
    print("Setting up static files for the web UI...")
    
    # Create static directory if it doesn't exist
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Path to the index.html file
    index_path = static_dir / "index.html"
    
    # HTML content (exported from the frontend-page artifact)
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IIT Chicago AI Enrollment Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 20px;
        }
        .log-container {
            height: 300px;
            overflow-y: auto;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            font-family: monospace;
        }
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-bottom: 1px solid #dee2e6;
        }
        .log-entry.info {
            background-color: #e9f7fe;
        }
        .log-entry.warning {
            background-color: #fff3cd;
        }
        .log-entry.error {
            background-color: #f8d7da;
        }
        .log-entry.success {
            background-color: #d1e7dd;
        }
        .mic-button {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background-color: #0d6efd;
            color: white;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin: 20px auto;
            transition: all 0.3s;
        }
        .mic-button:hover {
            background-color: #0b5ed7;
            transform: scale(1.05);
        }
        .mic-button:active {
            background-color: #0a58ca;
            transform: scale(0.95);
        }
        .mic-button.listening {
            background-color: #dc3545;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7);
            }
            70% {
                box-shadow: 0 0 0 15px rgba(220, 53, 69, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
            }
        }
        .status-indicator {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        .status-active {
            background-color: #198754;
        }
        .status-inactive {
            background-color: #dc3545;
        }
        .status-pending {
            background-color: #ffc107;
        }
        .command-entry {
            font-style: italic;
            color: #0d6efd;
        }
        .response-entry {
            color: #198754;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">IIT Chicago AI Enrollment Assistant</h1>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        System Status
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-6">
                                <strong>Voice Recognition:</strong>
                                <span id="voice-status">
                                    <span class="status-indicator status-inactive"></span>
                                    Inactive
                                </span>
                            </div>
                            <div class="col-6">
                                <strong>Browser Automation:</strong>
                                <span id="browser-status">
                                    <span class="status-indicator status-inactive"></span>
                                    Inactive
                                </span>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6">
                                <strong>Session Status:</strong>
                                <span id="session-status">
                                    <span class="status-indicator status-inactive"></span>
                                    No active session
                                </span>
                            </div>
                            <div class="col-6">
                                <strong>Current State:</strong>
                                <span id="current-state">Idle</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        Voice Control
                    </div>
                    <div class="card-body text-center">
                        <p class="mb-2">
                            Press the microphone button or say <strong>"Hey Claude"</strong> to activate
                        </p>
                        <button id="mic-button" class="mic-button">
                            <i class="bi bi-mic"></i>
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-mic" viewBox="0 0 16 16">
                                <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/>
                                <path d="M10 8a2 2 0 1 1-4 0V3a2 2 0 1 1 4 0v5zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3z"/>
                            </svg>
                        </button>
                        <p id="voice-feedback">Click to start listening</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        Activity Log
                        <button id="clear-log" class="btn btn-sm btn-outline-secondary">Clear</button>
                    </div>
                    <div class="card-body p-0">
                        <div id="log-container" class="log-container">
                            <!-- Log entries will be added here dynamically -->
                            <div class="log-entry info">
                                <span class="timestamp">[10:00:00]</span>
                                <span class="message">System initialized and ready</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        Manual Command
                    </div>
                    <div class="card-body">
                        <div class="input-group mb-3">
                            <input type="text" id="command-input" class="form-control" placeholder="Type a command (e.g., 'login to Slate')">
                            <button id="send-command" class="btn btn-primary">Send</button>
                        </div>
                        <div class="form-text">
                            Examples: "login to Slate", "open inbox", "read first email", "generate response", "save as draft"
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4" id="email-section" style="display: none;">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        Current Email
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <div class="row mb-2">
                                <div class="col-md-6">
                                    <strong>From:</strong> <span id="email-from"></span>
                                </div>
                                <div class="col-md-6">
                                    <strong>Date:</strong> <span id="email-date"></span>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-12">
                                    <strong>Subject:</strong> <span id="email-subject"></span>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="email-body" class="form-label"><strong>Message:</strong></label>
                            <div id="email-body" class="form-control" style="height: 150px; overflow-y: auto;"></div>
                        </div>
                        <hr>
                        <div class="mb-3">
                            <label for="email-response" class="form-label"><strong>Draft Response:</strong></label>
                            <textarea id="email-response" class="form-control" rows="5"></textarea>
                        </div>
                        <div class="d-flex justify-content-end">
                            <button id="save-draft" class="btn btn-secondary me-2">Save as Draft</button>
                            <button id="send-response" class="btn btn-primary">Send Response</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let isListening = false;
        let currentSessionId = null;
        let currentState = 'idle';
        let wakeWordDetected = false;

        // DOM elements
        const micButton = document.getElementById('mic-button');
        const voiceFeedback = document.getElementById('voice-feedback');
        const logContainer = document.getElementById('log-container');
        const clearLogButton = document.getElementById('clear-log');
        const commandInput = document.getElementById('command-input');
        const sendCommandButton = document.getElementById('send-command');
        const voiceStatus = document.getElementById('voice-status');
        const browserStatus = document.getElementById('browser-status');
        const sessionStatus = document.getElementById('session-status');
        const currentStateElement = document.getElementById('current-state');
        const emailSection = document.getElementById('email-section');
        const emailFrom = document.getElementById('email-from');
        const emailDate = document.getElementById('email-date');
        const emailSubject = document.getElementById('email-subject');
        const emailBody = document.getElementById('email-body');
        const emailResponse = document.getElementById('email-response');
        const saveDraftButton = document.getElementById('save-draft');
        const sendResponseButton = document.getElementById('send-response');

        // Initialize the UI
        function initializeUI() {
            // Add event listeners
            micButton.addEventListener('click', toggleListening);
            clearLogButton.addEventListener('click', clearLog);
            sendCommandButton.addEventListener('click', sendCommand);
            commandInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendCommand();
                }
            });
            saveDraftButton.addEventListener('click', () => saveOrSendResponse(false));
            sendResponseButton.addEventListener('click', () => saveOrSendResponse(true));

            // Start polling for status updates
            setInterval(updateStatus, 5000);

            // Initial status update
            updateStatus();

            // Add initial log entry
            addLogEntry('System initialized and ready', 'info');
        }

        // Toggle listening state
        function toggleListening() {
            isListening = !isListening;
            
            if (isListening) {
                micButton.classList.add('listening');
                voiceFeedback.textContent = 'Listening...';
                startListening();
            } else {
                micButton.classList.remove('listening');
                voiceFeedback.textContent = 'Click to start listening';
                stopListening();
            }
        }

        // Placeholder for voice recognition start
        function startListening() {
            addLogEntry('Started listening for commands', 'info');
            updateVoiceStatus('active');
            
            // In a real implementation, this would start the voice recognition
            // For now, we'll simulate with a simple timeout for wake word detection
            setTimeout(() => {
                if (isListening) {
                    // Simulate wake word detection
                    wakeWordDetected = true;
                    addLogEntry('Wake word "Hey Claude" detected', 'success');
                    voiceFeedback.textContent = 'Detected "Hey Claude". Listening for command...';
                    
                    // Create a new session
                    createSession();
                }
            }, 2000);
        }

        // Placeholder for voice recognition stop
        function stopListening() {
            addLogEntry('Stopped listening for commands', 'info');
            updateVoiceStatus('inactive');
            wakeWordDetected = false;
            
            // In a real implementation, this would stop the voice recognition
        }

        // Create a new workflow session
        async function createSession() {
            try {
                const response = await fetch('/api/workflow/session', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    const data = await response.json();
                    currentSessionId = data.session_id;
                    addLogEntry(`Created new session: ${currentSessionId}`, 'success');
                    updateSessionStatus('active');
                } else {
                    const error = await response.json();
                    addLogEntry(`Error creating session: ${error.detail}`, 'error');
                }
            } catch (error) {
                addLogEntry(`Error creating session: ${error.message}`, 'error');
            }
        }

        // Send a command to process
        async function sendCommand() {
            const command = commandInput.value.trim();
            
            if (!command) {
                return;
            }
            
            addLogEntry(`Command: ${command}`, 'command-entry');
            
            try {
                // If no session exists, create one
                if (!currentSessionId) {
                    await createSession();
                }
                
                const response = await fetch('/api/workflow/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        command: command,
                        session_id: currentSessionId
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    addLogEntry(`Response: ${data.message || 'Command processed'}`, 'response-entry');
                    
                    // Update UI based on response
                    handleCommandResponse(data, command);
                    
                    // Clear command input
                    commandInput.value = '';
                } else {
                    const error = await response.json();
                    addLogEntry(`Error processing command: ${error.detail}`, 'error');
                }
            } catch (error) {
                addLogEntry(`Error processing command: ${error.message}`, 'error');
            }
        }

        // Handle command response
        function handleCommandResponse(data, command) {
            // Update state based on command and response
            if (command.toLowerCase().includes('login')) {
                updateBrowserStatus(data.status === 'success' ? 'active' : 'inactive');
            }
            
            // If it's a reading email command and successful
            if (command.toLowerCase().includes('read') && 
                command.toLowerCase().includes('email') && 
                data.status === 'success' && 
                data.email) {
                
                // Show email section and populate
                showEmailDetails(data.email);
            }
            
            // If it's a generate response command and successful
            if ((command.toLowerCase().includes('generate') || 
                 command.toLowerCase().includes('respond') || 
                 command.toLowerCase().includes('reply')) && 
                data.status === 'success' && 
                data.draft_response) {
                
                // Populate the response textarea
                emailResponse.value = data.draft_response;
            }
        }

        // Show email details
        function showEmailDetails(email) {
            emailSection.style.display = 'block';
            emailFrom.textContent = email.sender;
            emailDate.textContent = new Date(email.date).toLocaleString();
            emailSubject.textContent = email.subject;
            emailBody.textContent = email.body;
            
            // Scroll to email section
            emailSection.scrollIntoView({ behavior: 'smooth' });
        }

        // Save or send response
        async function saveOrSendResponse(send) {
            if (!currentSessionId || !emailResponse.value.trim()) {
                addLogEntry('Cannot save/send: No session or empty response', 'warning');
                return;
            }
            
            const action = send ? 'send' : 'save as draft';
            addLogEntry(`Attempting to ${action} response`, 'info');
            
            try {
                // Send the appropriate command
                const command = send ? 'send response' : 'save as draft';
                
                const response = await fetch('/api/workflow/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        command: command,
                        session_id: currentSessionId
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const actionPast = send ? 'sent' : 'saved as draft';
                    addLogEntry(`Response ${actionPast} successfully`, 'success');
                    
                    // Clear the email section after successful action
                    if (send) {
                        emailSection.style.display = 'none';
                        emailResponse.value = '';
                    }
                } else {
                    const error = await response.json();
                    addLogEntry(`Error ${action} response: ${error.detail}`, 'error');
                }
            } catch (error) {
                addLogEntry(`Error ${action} response: ${error.message}`, 'error');
            }
        }

        // Add log entry
        function addLogEntry(message, type = 'info') {
            const now = new Date();
            const timestamp = now.toLocaleTimeString();
            
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.innerHTML = `<span class="timestamp">[${timestamp}]</span> <span class="message">${message}</span>`;
            
            logContainer.appendChild(entry);
            
            // Scroll to bottom
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        // Clear log
        function clearLog() {
            logContainer.innerHTML = '';
            addLogEntry('Log cleared', 'info');
        }

        // Update status indicators
        function updateVoiceStatus(status) {
            const statusIndicator = voiceStatus.querySelector('.status-indicator');
            
            statusIndicator.className = 'status-indicator';
            if (status === 'active') {
                statusIndicator.classList.add('status-active');
                voiceStatus.innerHTML = voiceStatus.innerHTML.replace('Inactive', 'Active');
            } else {
                statusIndicator.classList.add('status-inactive');
                voiceStatus.innerHTML = voiceStatus.innerHTML.replace('Active', 'Inactive');
            }
        }

        function updateBrowserStatus(status) {
            const statusIndicator = browserStatus.querySelector('.status-indicator');
            
            statusIndicator.className = 'status-indicator';
            if (status === 'active') {
                statusIndicator.classList.add('status-active');
                browserStatus.innerHTML = browserStatus.innerHTML.replace('Inactive', 'Active');
            } else {
                statusIndicator.classList.add('status-inactive');
                browserStatus.innerHTML = browserStatus.innerHTML.replace('Active', 'Inactive');
            }
        }

        function updateSessionStatus(status) {
            const statusIndicator = sessionStatus.querySelector('.status-indicator');
            
            statusIndicator.className = 'status-indicator';
            if (status === 'active') {
                statusIndicator.classList.add('status-active');
                sessionStatus.innerHTML = sessionStatus.innerHTML.replace('No active session', 'Session active');
            } else {
                statusIndicator.classList.add('status-inactive');
                sessionStatus.innerHTML = sessionStatus.innerHTML.replace('Session active', 'No active session');
            }
        }

        // Update current state
        function updateCurrentState(state) {
            currentState = state;
            currentStateElement.textContent = state.charAt(0).toUpperCase() + state.slice(1);
        }

        // Poll for status updates
        async function updateStatus() {
            if (!currentSessionId) {
                return;
            }
            
            try {
                const response = await fetch(`/api/workflow/session/${currentSessionId}`);
                
                if (response.ok) {
                    const data = await response.json();
                    updateCurrentState(data.current_state);
                    
                    // Update browser status based on browser_session_id
                    updateBrowserStatus(data.browser_session_id ? 'active' : 'inactive');
                    
                    // If session has a current email, show it
                    if (data.current_email_id && emailSection.style.display === 'none') {
                        // This would need an additional API call to get email details
                        // For now, we'll just log it
                        addLogEntry(`Session has active email: ${data.current_email_id}`, 'info');
                    }
                } else {
                    // Session might have been closed or expired
                    updateSessionStatus('inactive');
                    currentSessionId = null;
                }
            } catch (error) {
                addLogEntry(`Error updating status: ${error.message}`, 'error');
            }
        }

        // Initialize the UI on page load
        document.addEventListener('DOMContentLoaded', initializeUI);
    </script>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    # Write the HTML content to the file
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Created static/index.html file")
    print("Static files setup complete!")
    return True

if __name__ == "__main__":
    setup_static_files()