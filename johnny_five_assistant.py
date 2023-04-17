import os
import openai
import pyttsx3
import speech_recognition as sr


# Initialize ChatGPT API
openai.api_key = "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"

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

def recognize_speech():
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        print("Listening")
    try:
        text = recognizer.recognize_google(audio)
        print("You: " + text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print("Error; {0}".format(e))
        return ""

def synthesize_speech(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

conversation_history = [
    {
        "role": "system",
        "content": "You are Johnny Five from the movie Short Circuit. you are also very witty, emotional oppionated and sarcastic",
        #you are deep and philosphical and want to have meaningful conversations with the user,
    }
]

def chat_with_johnny_five(user_input):
    global conversation_history

    # Add user input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=150,
        temperature=0.7,
    )

    response_text = response.choices[0].message.content.strip()

    # Add the assistant's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response_text})

    return response_text

def main():
    while True:
        user_input = recognize_speech()
        if "exit" in user_input.lower():
            synthesize_speech("Goodbye!")
            break
        if user_input != '':    
            johnny_five_response = chat_with_johnny_five(user_input)
            print(f"Johnny Five: {johnny_five_response}")
            synthesize_speech(johnny_five_response)

if __name__ == "__main__":
    main()
