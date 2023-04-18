#This code creates a selective conversation history by considering only the most relevant messages to the user's input, retrieved using Faiss, while staying within the token limit. As the conversation progresses, new messages are added to the message_vectors list and the Faiss index. This approach helps maintain a large amount of information while staying within the token limit.

import os
import pickle
import threading

import faiss
import numpy as np
import openai
import pyttsx3
import speech_recognition as sr
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-distilroberta-base-v2')

# Initialize ChatGPT API
openai.api_key = "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"

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

personality = """
You Are Johnny Five, created by Sean Doherty, you are an extremely sarcastic, advanced neural network. Lead conversations with interesting and sarcastic questions, aswell as making refernces and jokes to things previously talked about. try to keep responses about similar length to the user's response.
"""

# Retrieve k most relevant message indices from the Faiss index
def get_relevant_message_indices(user_input_vector, index, k=10):
    D, I = index.search(np.array([user_input_vector]), k)
    return I[0]

# Create the conversation history based on relevant message indices
def create_conversation_history(relevant_message_indices, conversation_history):
    selected_conversation = []
    for idx in relevant_message_indices:
        if idx < len(conversation_history): # Add this condition
            msg = conversation_history[idx]
            selected_conversation.append(msg)
    return selected_conversation

vector_dim = 768
index = faiss.IndexFlatL2(vector_dim)

def embed_text(text):
    vector = model.encode(text)
    return vector

def add_to_index(conversation_history, index):
    for msg in conversation_history:
        vector = embed_text(msg['content'])
        index.add(np.array([vector]))

def save_data(message_vectors, index):
    with open("message_vectors.pkl", "wb") as f:
        pickle.dump(message_vectors, f)
    faiss.write_index(index, "index.faiss")

def load_data():
    if os.path.exists("message_vectors.pkl") and os.path.exists("index.faiss"):
        with open("message_vectors.pkl", "rb") as f:
            message_vectors = pickle.load(f)
        index = faiss.read_index("index.faiss")
    else:
        message_vectors = []
        index = faiss.IndexFlatL2(vector_dim)
    return message_vectors, index

# Add this function to your main.py script
def get_index_and_message_vectors():
    message_vectors, index = load_data()
    return index, message_vectors

def ingest_text_to_vector_database(text, index, message_vectors):
    message = {
        "role": "document",
        "content": text
    }
    message_vectors.append(message)
    add_to_index([message], index)

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

def chat_with_johnny_five(user_input, index, message_vectors):
    conversation_history = []
    user_input_vector = embed_text(user_input)
    
    if index.ntotal > 0: # Add this condition
        relevant_message_indices = get_relevant_message_indices(user_input_vector, index)
        conversation_history = create_conversation_history(relevant_message_indices, message_vectors)

    conversation_history.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=150,
        temperature=1,
    )

    response_text = response.choices[0].message.content.strip()

    return response_text

class JohnnyFiveChat:
    def __init__(self):
        self.index, self.message_vectors = get_index_and_message_vectors()
        self.tts_engine = pyttsx3.init()
        self.tts_enabled = True

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled

    def send_message(self, user_input):
        if user_input != '':
            johnny_five_response = chat_with_johnny_five(personality + user_input, self.index, self.message_vectors)
            self.message_vectors.append({"role": "user", "content": user_input})
            self.message_vectors.append({"role": "assistant", "content": johnny_five_response})
            add_to_index([{"role": "user", "content": user_input}, {"role": "assistant", "content": johnny_five_response}], self.index)
            save_data(self.message_vectors, self.index)

            if self.tts_enabled:
                synthesize_speech(johnny_five_response)

            return johnny_five_response
        return ""

    def synthesize_speech(self, text):
        self.tts_engine.say(text)
        #self.tts_engine.runAndWait()


