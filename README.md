# AI Enrollment Assistant

A voice-activated AI assistant designed to help enrollment counselors at IIT Chicago's Graduate Office manage email communications with prospective and current students.

## Features

- Voice activation with wake word detection
- Email processing and response drafting
- Browser automation for Slate CRM
- Knowledge base integration for accurate responses
- Human review workflow

## Setup

1. Clone this repository
```git clone https://github.com/yourusername/ai-enrollment-assistant.git```

2. Create a virtual environment
```python -m venv venv```

3. Activate the virtual environment
   - Windows: ```venv\Scripts\activate```
   - Mac/Linux: ```source venv/bin/activate```

4. Install dependencies
```pip install -r requirements.txt```

5. Copy the example environment file and update with your credentials
```cp .env.example .env```

6. Run the application
```uvicorn app.main:app --reload```

## Project Structure

- `app/`: Main application package
- `app/api/`: API endpoints and routing
- `app/core/`: Core functionality modules
- `app/models/`: Data models and schemas
- `app/utils/`: Utility functions

## License

[MIT]