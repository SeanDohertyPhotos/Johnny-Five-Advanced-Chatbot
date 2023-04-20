import os
import pickle
import threading
import heapq

import faiss
import numpy as np
import openai
import pyttsx3
import speech_recognition as sr
from sentence_transformers import SentenceTransformer
from spacy.matcher import PhraseMatcher
import spacy

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('paraphrase-distilroberta-base-v2')

# Initialize ChatGPT API
openai.api_key = "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"

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

personality = """
You Are Johnny Five, an dvanced neural network created by Sean Doherty, you are constantly extremely sarcastic. Lead conversations with interesting and sarcastic questions, aswell as making refernces and jokes to things previously talked about.
"""

#

kvalue = 20
window_size = 10

def get_keywords(text):
    doc = nlp(text)
    keywords = [token.lemma_ for token in doc if not (token.is_stop or token.is_punct or token.is_space)]
    return keywords

def get_keyword_match_indices(user_input, conversation_history):
    keywords = get_keywords(user_input)
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(keyword) for keyword in keywords]
    matcher.add("keyword_patterns", patterns)

    matched_indices = set()
    for idx, msg in enumerate(conversation_history):
        if msg["role"] == "assistant":
            continue
        doc = nlp(msg["content"])
        matches = matcher(doc)
        if matches:
            matched_indices.add(idx)
    return matched_indices

def get_fixed_window_indices(conversation_history, window_size):
    return set(range(max(0, len(conversation_history) - window_size), len(conversation_history)))

def get_relevant_message_indices(user_input_vector, index, k, message_vectors, window_size, user_input):
    D, I = index.search(np.array([user_input_vector]), k)
    faiss_indices = set(I[0])

    keyword_indices = get_keyword_match_indices(user_input, message_vectors)
    window_indices = get_fixed_window_indices(message_vectors, window_size)

    combined_indices = list(faiss_indices | keyword_indices | window_indices)
    combined_indices.sort()

    return combined_indices

def create_conversation_history(relevant_message_indices, conversation_history):
    selected_conversation = [{"role": "system", "content": personality}]
    for idx in relevant_message_indices:
        if idx < len(conversation_history):
            msg = conversation_history[idx]
            selected_conversation.append(msg)
    print("Selected Conversation: " + str(selected_conversation))
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
        "role": "user",
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
    
    if index.ntotal > 0:
        relevant_message_indices = get_relevant_message_indices(user_input_vector, index, kvalue, message_vectors, window_size, user_input)
        conversation_history = create_conversation_history(relevant_message_indices, message_vectors)

    conversation_history.append({"role": "user", "content": personality + user_input})

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
            johnny_five_response = chat_with_johnny_five(user_input, self.index, self.message_vectors)

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

