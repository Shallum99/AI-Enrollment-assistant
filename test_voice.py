import speech_recognition as sr

def test_microphone():
    """Simple test to check if microphone is working"""
    recognizer = sr.Recognizer()
    
    print("Microphone test - please speak after 'Listening...'")
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)
        
    try:
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        return True
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Request error: {e}")
    
    return False

if __name__ == "__main__":
    test_microphone()