import requests
import random
import static.data as data
import streamlit as st


def record_text(text_to_speak: str, voice_type: str, chunk_size = 1024, path = "voice/voice1.mp3"):
    output_path = "static/music/" + path
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
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)

        return {"status": "success", "detail": output_path}
    
    return {"status": "error", "detail": response.text}


def play_record_text(voice_type: str, prompt: str, path=None):
    if not path:
        voice_number = data.get_count_in_folder("static/music/voice/") + 1
        voice_dict = record_text(prompt, data.voice_types[voice_type], path=f"voice/voice{voice_number}.mp3")
    else:
        voice_dict = record_text(prompt, data.voice_types[voice_type], path=path)

    if voice_dict["status"] == "success":
        path_to_voice = voice_dict["detail"]
        audio_file = open(path_to_voice, "rb")
        audio_bytes = audio_file.read()

        st.audio(audio_bytes, format="audio/ogg")
    return path_to_voice


def play_audio(state, location):
    random_n = str(random.randint(1, 3))
    if state == "По умолчанию":
        audio_file = open(f"static/music/locations/{data.locations[location]}/{data.locations[location]}.mp3", "rb")
    else:
        audio_file = open(f"static/music/{data.states[state]}/{data.states[state]}{random_n}.mp3", "rb")

    audio_bytes = audio_file.read()    
    st.audio(audio_bytes, format="audio/ogg")