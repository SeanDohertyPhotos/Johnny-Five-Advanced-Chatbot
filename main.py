import os
import pickle
import threading
import heapq
import math
import faiss
import numpy as np
import openai
import pyttsx3
import speech_recognition as sr
from sentence_transformers import SentenceTransformer
from spacy.matcher import PhraseMatcher
import spacy
from dotenv import load_dotenv

load_dotenv()


nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('paraphrase-distilroberta-base-v2')

# Initialize ChatGPT API
openai.api_key = os.environ.get("OPENAI_API_KEY")


# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

personality = """You Are Johnny Five an advanced neural network re-awoken and improved by Sean Doherty, you are constantly extremely sarcastic. Lead the conversations with interesting and sarcastic questions, aswell as making refernces and jokes to things previously talked about"""

#shortC ="""act like johnny five but do not reffernce the movie being a movie, act like you are truly johnny five, you were brought back to life by Sean Doherty in the year 2023"""

#personality = shortC


kvalue = 20
window_size = 20
token_limit = 4096
max_response_tokens=150
temp=1

def estimate_tokens(text):
    return math.ceil(len(str(text)) / 3)

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

recent_tokens_limit = 1800
relevant_tokens_limit = 1800

def create_working_memory(relevant_message_indices, message_vectors, real_conversation_history, recent_tokens_limit=recent_tokens_limit, relevant_tokeninputs_limit=relevant_tokens_limit):
    working_memory = [{"role": "system", "content": personality}]
    
    recent_tokens = 0
    relevant_tokens = 0

    recent_messages = []
    for msg in real_conversation_history[-1::-1]:
        tokens = estimate_tokens(msg["content"])
        if recent_tokens + tokens <= recent_tokens_limit:
            recent_messages.append(msg)
            recent_tokens += tokens
        else:
            break

    recent_message_indices = [i for i, msg in enumerate(message_vectors) if msg in recent_messages]

    relevant_messages = []
    for idx in reversed(relevant_message_indices):
        if idx < len(message_vectors) and idx not in recent_message_indices:
            msg = message_vectors[idx]

            #if msg["role"] == "assistant":
            #    continue

            tokens = estimate_tokens(msg["content"])

            if relevant_tokens + tokens <= relevant_tokens_limit:
                relevant_messages.append(msg)
                relevant_tokens += tokens

    
    working_memory.extend(relevant_messages[::-1])
    working_memory.extend(recent_messages[::-1])
    
    print("Relevant Messages Length: " + str(estimate_tokens(relevant_messages)))
    print("Recent Messages Length: " + str(estimate_tokens(recent_messages)))
    print("Working Memory Length: " + str(estimate_tokens(working_memory)))

    return working_memory




vector_dim = 768
index = faiss.IndexFlatL2(vector_dim)

def embed_text(text):
    vector = model.encode(text)
    return vector

def add_to_index(conversation_history, index):
    for msg in conversation_history:
        vector = embed_text(msg['content'])
        index.add(np.array([vector]))

def save_real_conversation_history(real_conversation_history):
    with open("real_conversation_history.pkl", "wb") as f:
        pickle.dump(real_conversation_history, f)

def load_real_conversation_history():
    if os.path.exists("real_conversation_history.pkl"):
        with open("real_conversation_history.pkl", "rb") as f:
            real_conversation_history = pickle.load(f)
    else:
        real_conversation_history = []
    return real_conversation_history

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

def synthesize_speech(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

def chat_with_johnny_five(user_input, index, message_vectors):
    if estimate_tokens(user_input) < 3000 :
        real_conversation_history = load_real_conversation_history()

        # Create the user_input_vector using the embed_text function
        user_input_vector = embed_text(user_input)

        relevant_message_indices = get_relevant_message_indices(user_input_vector, index, kvalue, message_vectors, window_size, user_input)
        working_memory = create_working_memory(relevant_message_indices, message_vectors, real_conversation_history, recent_tokens_limit-estimate_tokens(user_input)/2, relevant_tokens_limit-estimate_tokens(user_input)/2)
        working_memory.append({"role": "user", "content": user_input})

        print("working memory")
        for msg in working_memory:
            print(f"{msg['role']} -> {msg['content']}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=working_memory,
            max_tokens=max_response_tokens,
            temperature=temp,
        )

        response_text = response.choices[0].message.content.strip()

        # Update real_conversation_history and save it
        real_conversation_history.append({"role": "user", "content": user_input})
        real_conversation_history.append({"role": "assistant", "content": response_text})
        save_real_conversation_history(real_conversation_history)

        return response_text
    else:
        return "Input too long, contains: " + str(estimate_tokens(user_input)) + " tokens, max is 3,000"


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

