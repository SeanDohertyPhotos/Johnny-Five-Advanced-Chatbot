import speech_recognition as sr
import pyttsx3
from api_connections import chat_gpt, weather
from intents import process_message, create_prompt

def record_audio(recognizer, microphone):
    with microphone as source:
        print("Recording...")
        audio = recognizer.listen(source)
        print("Finished recording.")
    return audio

def handle_message(message):
    intent, parameters = process_message(message)
    prompt = create_prompt(intent, parameters, message)
    response_text = chat_gpt.call_chat_gpt(prompt)

    return response_text

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    engine = pyttsx3.init()

    while True:
        # Record audio from the user
        audio_data = record_audio(recognizer, microphone)

        # Transcribe the user's speech
        try:
            user_text = recognizer.recognize_google(audio_data)
            print(f"User said: {user_text}")

            # Handle the user's message and get a response
            response_text = handle_message(user_text)
            print(f"Assistant said: {response_text}")

            # Synthesize the assistant's response
            engine.say(response_text)
            engine.runAndWait()

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    main()
