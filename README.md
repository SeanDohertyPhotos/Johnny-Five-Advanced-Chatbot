#Johnny Five Chatbot
This project is an implementation of a chatbot named Johnny Five, which is built using OpenAI's GPT-3.5-turbo model. The chatbot's working memory consists of a novel hybrid memory system that combines a token buffer memory and a locally stored vector database semantic search to provide more accurate and context-aware responses. effectively gving Johnny unlimited memory while keeping a steady conversation flow. 

#Table of Contents
- [Features](#features)
- [Requirements](#Requirements)
- [Installation](#Installation)
- [Usage](#Usage)
- [Understanding the Code](#Understanding-the-code)
- [Contributing](#Contributing)
- [License](#License)

##Features
- A novel hybrid memory system that combines token buffer memory and a locally stored vector database semantic search.
- A simple graphical user interface (GUI) for interactive conversations.
- Text-to-speech (TTS) integration for the chatbot's responses.
- The ability to store conversation history for context and recall.

##Requirements
- Python 3.6 or higher
- OpenAI Python (v0.27.0)
- FAISS (v1.7.1)
- Sentence Transformers (v2.1.0)
- spaCy (v3.2.0)
- python-dotenv (v0.19.1)
- pyttsx3 (v2.90)
- SpeechRecognition (v3.8.1)
- Tkinter (built-in)

##Installation
- Clone the repository:
```
git clone https://github.com/your_username/JohnnyFiveChatbot.git
```
- Navigate to the project directory:
```
cd JohnnyFiveChatbot
```
- Install requirements
```
pip install -r requirements.txt
```
- Modify .env file in the project directory and add your OpenAI API key:

OPENAI_API_KEY=your_api_key_here
Usage
- Run the chatbot application:
```
python gui.py
```
A GUI window will appear, allowing you to chat with Johnny Five. You can type your message in the input box and press "Send" or hit the Enter key to send it. The chatbot will respond with its message, synthesized using its hybrid memory system.

##Understanding the Code
The code is organized into two main parts:

- The core chatbot logic and hybrid memory system implementation (main.py).
- The graphical user interface implementation (gui.py).
Core Chatbot Logic and Hybrid Memory System
The main.py file contains the implementation of the chatbot and its hybrid memory system. The JohnnyFiveChat class is responsible for managing the chatbot's working memory and generating responses using the GPT-3.5-turbo model.

The hybrid memory system uses token buffer memory to store recent conversation tokens and a locally stored vector database for semantic search. The memory system leverages the FAISS library for efficient nearest neighbor search and the Sentence-Transformers library for creating sentence embeddings. The hybrid memory system helps Johnny Five, the chatbot, provide more context-aware and relevant responses.

###Here's a detailed breakdown of the core components and functions in main.py:

- **Import libraries and load models:** The required libraries and models are imported, including OpenAI's GPT-3.5-turbo model and the SentenceTransformer model.

- **Initialize API keys and engines:** The OpenAI API key, and text-to-speech engines are initialized.

- **Define constants:** Several constants are defined, including k-value, window size, token limit, and max response tokens.

- **Helper functions:** A set of helper functions is defined to perform tasks such as estimating tokens, getting keywords, creating the working memory, and managing the FAISS index.

- **Embedding text:** The embed_text() function is used to create sentence embeddings using the SentenceTransformer model.

- **Loading and saving data:** Functions to load and save real_conversation_history, message_vectors, and the FAISS index are defined.

- **Synthesizing speech:** The synthesize_speech() function is used to convert text to speech using the pyttsx3 library.

- **Chat with Johnny Five:** The chat_with_johnny_five() function is the main function that takes user input, creates working memory, generates a response using the GPT-3.5-turbo model, and updates the real_conversation_history.

- **JohnnyFiveChat class:** This class manages the chatbot's hybrid memory system, enabling text-to-speech, and sending messages.

- **Graphical User Interface (gui.py)**
The UI.py file contains the implementation of the graphical user interface using the Tkinter library. The JohnnyFiveApp class creates the chat window, input text entry, and buttons to send messages and toggle text-to-speech functionality. The class also handles sending and receiving messages, updating the chat area, and binding keyboard shortcuts.

To use the chatbot, simply run the gui.py script, which will display the Johnny Five chat window. Type your message into the input box and press Enter or click the Send button to receive a response from Johnny Five.

##Contributing
If you want to contribute that'd be great. I'd really like to recreate this bot and memory technique on langchain so that I could easily implement things like agents and search to it. but could use help with that. 