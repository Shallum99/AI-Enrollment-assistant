# run_minimal.py
"""
Minimal starter version of the run.py file.
This runs the minimal version of the app without requiring all modules.
"""
import uvicorn
import os

if __name__ == "__main__":
    print("Starting AI Enrollment Assistant API (minimal version)")
    print("Access the API at http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")
    
    uvicorn.run(
        "app.main_minimal:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        log_level="info"
    )