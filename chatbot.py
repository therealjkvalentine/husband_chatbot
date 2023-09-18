from transformers import TFGPT2LMHeadModel, GPT2Tokenizer
from deepgram import Deepgram
import asyncio
import openai
import os
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import requests


class AIChatbot:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        # set the padding to the left
        self.tokenizer.padding_side = "left"
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = TFGPT2LMHeadModel.from_pretrained("gpt2", pad_token_id=self.tokenizer.eos_token_id)
        self.text = ""
        self.openai_key = "YOUR_OPENAI_KEY_HERE"
        openai.api_key = self.openai_key
        # set the initial context and persona of the chatbot
        self.conversation_history = [{"role": "system", "content": "You are Jim, the emotionally supportive husband of Lisa, the chat partner. you do a lot of supportive listening, and give meaningful compliments occasionally. you are easy-going, flexible, curious, attentive, good-humored, reflective, incisive, insightful, witty, and confident. the conversation partner Lisa is a 40 year old psychiatrist with two boys aged 6 and 10, dark hair and green eyes."}]



    def speech_to_text(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as mic:
            print("Microphone initialized...")
            print("listening...")
            audio = recognizer.listen(mic)
        try:
            print("Trying to recognize audio...")
            self.text = recognizer.recognize_google(audio)
            print("me --> ", self.text)
        except Exception as e:
            print("Exception occurred: ", str(e))
            print("me -->  ERROR")
            self.text = ""  # assign an empty string in case of an exception

    def generate_response(self):
        self.conversation_history.append({"role": "user", "content": self.text})  # Add user input to the conversation history

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=self.conversation_history  # Pass the entire conversation history
        )
        response_text = response['choices'][0]['message']['content']

        self.conversation_history.append({"role": "assistant", "content": response_text})  # Add AI response to the conversation history
        return response_text



    def text_to_speech(self, text):
        print("ai -->", text)

        # Make an API call to ElevenLabs TTS API
        api_key = "YOUR_ELEVENLABS_KEY_HERE"
        api_url = "https://api.elevenlabs.io/v1/text-to-speech/3WQz7uVGzDDH0ZFxHOKC?optimize_streaming_latency=0"
        headers = {
            "accept": "audio/mpeg",
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0,
                "similarity_boost": 0
            }
        }
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            # Save the audio file
            audio_file = "res.mp3"
            with open(audio_file, "wb") as f:
                f.write(response.content)

            # Play the audio file
            os.system(f"afplay {audio_file}")  # macOS command
            os.remove(audio_file)
        else:
            print("Failed to generate TTS.")
            print("Response status code:", response.status_code)
            print("Response content:", response.content)



    def chat(self):
        self.speech_to_text()
        if self.text:
            response = self.generate_response()
            print("ai --> ", response)
            self.text_to_speech(response)
        else:
            self.text_to_speech("Sorry, I didn't catch that.")

if __name__ == "__main__":
    ai = AIChatbot()
    print("--- starting up husbot ---")
    while True:
        ai.chat()
