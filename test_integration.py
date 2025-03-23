import speech_recognition as sr
from playwright.sync_api import sync_playwright

def simple_voice_command():
    """Listen for a voice command and perform a browser action"""
    recognizer = sr.Recognizer()
    
    print("Say a command like 'open website' or 'navigate to Google'")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"Command recognized: {text}")
        
        # Simple command processing
        if "open website" in text.lower() or "navigate" in text.lower():
            url = "https://google.com"  # Default
            
            if "google" in text.lower():
                url = "https://google.com"
            elif "example" in text.lower():
                url = "https://example.com"
                
            # Execute browser action
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                print(f"Navigating to {url}...")
                page.goto(url)
                
                # Wait for user to see the result
                input("Press Enter to close the browser...")
                browser.close()
        else:
            print("Command not recognized. Try 'open website' or 'navigate to Google'")
            
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    simple_voice_command()