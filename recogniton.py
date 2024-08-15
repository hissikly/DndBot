import speech_recognition as sr

r = sr.Recognizer()

def va_listen():
    with sr.Microphone() as source:
        audio_text = r.listen(source)
        
        try:
            return r.recognize_google(audio_text, language="ru-RU")
        except:
            return ""