import openai
import os
import requests
import json
import time
import glob
import pygame

voices = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
}

OPENAI_API_KEY = 'OPENAI-APIKEY-HERE'
INPUT_DIR = "INPUT-DIR-HERE" # make your input wherever your audio program saves your files too.
OUTPUT_DIR = "OUTPUT-DIR-HERE" # use the directory of the output folder inside this repo
VOICE_ID = voices['Adam']
ELEVEN_LABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
HEADERS = {
    "xi-api-key": "ELEVENLABS-APIKEY-HERE",
    "Content-Type": "application/json"
}

openai.api_key = OPENAI_API_KEY

def convert_text_to_speech(text, output_filename):
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 1,
            "similarity_boost": 1
        }
    }

    
    response = requests.post(ELEVEN_LABS_URL, headers=HEADERS, data=json.dumps(payload))
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Error occurred while generating speech: {response.status_code}, {response.text}")
        return False
        

    
        

def transcribe_audio(file_path):
    print("Transcribing audio...")
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    text = transcript["text"]
    print("Transcription Finished, I got,", text, "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613", #use gpt-4 if you want idc, will be slower
        messages=[{"role": "user", "content": text}],
        max_tokens=70,
        temperature=0.5
    )
    print("Response Finished")
    response_text = response['choices'][0]['message']['content']
    print("Response -", response_text, "")
    output_filename = os.path.join(OUTPUT_DIR, "response.mp3")
    convert_text_to_speech(response_text, output_filename)
    os.remove(file_path)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    print("Playing audio...")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
       
    pygame.mixer.music.stop()
    print("Stopping audio...")
    print("Deleting Output File...")
    pygame.mixer.quit()
    time.sleep(1)
    os.remove(file_path)

def watch_for_new_audio():
    while True:
        pygame.mixer.init()
        seen_files = set()
        clear_console()
        print(f"Watching for new audio files in {INPUT_DIR}...")
        audio_files = glob.glob(os.path.join(INPUT_DIR, '*.m4a'))
        new_files = set(audio_files) - seen_files
        for audio_file_path in new_files:
            previous_size = -1
            while True:
                current_size = os.path.getsize(audio_file_path)
                if current_size == previous_size:
                    break
                previous_size = current_size
                time.sleep(1)
            transcribe_audio(audio_file_path)
            response_file_path = os.path.join(OUTPUT_DIR, "response.mp3")
            play_audio(response_file_path)
            seen_files.add(audio_file_path)
        time.sleep(0.5)

if __name__ == "__main__":
    watch_for_new_audio()
