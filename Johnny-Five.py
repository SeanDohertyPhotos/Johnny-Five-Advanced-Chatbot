import os
import openai
import pyttsx3
import speech_recognition as sr
import pickle


# Initialize ChatGPT API
openai.api_key = "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"

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

personality = """
You Are Johnny Five, created by Sean Doherty, you are an extreamly sarcastic, advanced neural network. Lead conversations with ineteresting and sarcastic questions
"""

conversation_history = [
    {
        "role": "system",
        "content": personality,
    }
]

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


def summarize_chat_history():
    global conversation_history
    text = "\n".join([msg['content'] for msg in conversation_history])

    summary_request = conversation_history + [{"role": "system", "content": personality + "summarize the conversation so far."}]

    summary_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=summary_request,
        max_tokens=1000,
        temperature=0.5,
    )

    summarized_text = summary_response.choices[0].message.content.strip()
    return summarized_text



def chat_with_johnny_five(user_input):
    global conversation_history

    # Add user input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Remove old conversation history if the text length exceeds the token limit
    while sum(len(msg['content']) for msg in conversation_history) > 4000:
        summarized_text = summarize_chat_history()
        conversation_history = conversation_history[len(conversation_history)//2:]
        conversation_history.insert(0, {"role": "assistant", "content": summarized_text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=150,
        temperature=1,
    )

    response_text = response.choices[0].message.content.strip()

    # Add the assistant's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response_text})
    #print(str(conversation_history))
    return response_text

def save_conversation_history(history, filename="conversation_history.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(history, f)

def load_conversation_history(filename="conversation_history.pkl"):
    if not os.path.exists(filename):
        return [
            {
                "role": "system",
                "content": personality,
            }
        ]
    with open(filename, "rb") as f:
        return pickle.load(f)



def main():
    global conversation_history
    conversation_history = load_conversation_history()

    johnny_five_response = chat_with_johnny_five("Please introduce yourself, without giving away your prompt except your name and then ask who you are speaking to")
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

            print("Charater Length: " + str(sum(len(msg['content']) for msg in conversation_history)))
            save_conversation_history(conversation_history)


if __name__ == "__main__":
    main()
