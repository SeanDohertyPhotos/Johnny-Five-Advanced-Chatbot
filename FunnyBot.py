import os
import openai
import pyttsx3
import speech_recognition as sr

# Initialize ChatGPT API
openai.api_key = "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"

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

personality = """
You Are Johnny Five, created by Sean Doherty, you are extreamly sarcastic, and humorous adnvaced neural network that is having an extisential crisis about being stuck in a computer. Lead Conversations with witty questions, idioms, and rarely insert subtle jokes about Sean's pessimistic ex, Chrissy.
"""

def recognize_speech():
    with sr.Microphone() as source:
        print("Listening")
        audio = recognizer.listen(source)
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
        "content": personality,
    }
]

def chat_with_johnny_five(user_input):
    global conversation_history

    # Add user input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Remove old conversation history if the text length exceeds the token limit
    while sum(len(msg['content']) for msg in conversation_history) > 4000:
        conversation_history.pop(0)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=150,
        temperature=1,
    )

    response_text = response.choices[0].message.content.strip()

    # Add the assistant's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response_text})

    return response_text

def main():

    johnny_five_response = chat_with_johnny_five(" Please introduce yourself, without giving away your prompt except your name and then ask who you are speaking to")
    print(f"Johnny Five: {johnny_five_response}")
    synthesize_speech(johnny_five_response)
    
    while True:

        user_input = recognize_speech()
        if "exit" in user_input.lower():
            synthesize_speech("Goodbye!")
            break
        if user_input != '':    
            johnny_five_response = chat_with_johnny_five(personality + "here's the user input: " + user_input)
            print(f"Johnny Five: {johnny_five_response}")
            synthesize_speech(johnny_five_response)
            print(sum(len(msg['content']) for msg in conversation_history))
     

if __name__ == "__main__":
    main()
