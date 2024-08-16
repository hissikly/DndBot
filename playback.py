import requests
import random
import static.data as data
import streamlit as st


def record_text(text_to_speak: str, voice_type: str):
    headers = {
        "Accept": "application/json",
        "xi-api-key": st.secrets["XI_API_KEY"]
    }

    data = {
        "text": text_to_speak,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    response = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_type}/stream", headers=headers, json=data, stream=True)

    if response.ok:
        print("1111")
        st.session_state.bytes_of_voices.append(response.content)

        return {"status": "success"}
    print("2222")
    return {"status": "error"}


def play_record_text(voice_type: str, prompt: str):
    voice_dict = record_text(prompt, data.voice_types[voice_type])
    
    if voice_dict["status"] == "success":
        print("33333")
        st.audio(st.session_state.bytes_of_voices[-1], format="audio/ogg")


def play_audio(state, location):
    random_n = str(random.randint(1, 3))
    if state == "По умолчанию":
        audio_file = open(f"static/music/locations/{data.locations[location]}/{data.locations[location]}.mp3", "rb")
    else:
        audio_file = open(f"static/music/{data.states[state]}/{data.states[state]}{random_n}.mp3", "rb")

    audio_bytes = audio_file.read()    
    st.audio(audio_bytes, format="audio/ogg")