from setuptools import setup, find_packages

setup(
    name="ai-enrollment-assistant",
    version="0.1.0",
    description="Voice-activated AI assistant for managing enrollment communications",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "SpeechRecognition>=3.10.0",
        "gTTS>=2.3.2",
        "pvporcupine>=2.2.0",
        "PyAudio>=0.2.13",
        "langchain>=0.0.267",
        "langchain-openai>=0.0.2",
        "openai>=1.0.0",
    ],
    python_requires=">=3.9",
)