import json
import os
import pickle
import tkinter as tk
from tkinter import filedialog

import docx
import nltk
import pandas as pd
import PyPDF2
from bs4 import BeautifulSoup

nltk.download('punkt')
from nltk.tokenize import sent_tokenize

from main import get_index_and_message_vectors, ingest_text_to_vector_database

index, message_vectors = get_index_and_message_vectors()

def ingest_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if isinstance(item, dict):
                    for key in item:
                        ingest_text_to_vector_database(item[key], index, message_vectors)
                elif isinstance(item, str):
                    ingest_text_to_vector_database(item, index, message_vectors)

    elif file_extension == '.html':
        with open(file_path, 'r') as f:
            soup = BeautifulSoup(f, 'lxml')
            text = soup.get_text(separator=' ')
            ingest_text_to_vector_database(text, index, message_vectors)

    elif file_extension in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path, engine='openpyxl')
        for _, row in df.iterrows():
            for value in row:
                ingest_text_to_vector_database(str(value), index, message_vectors)

    elif file_extension == '.docx':
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            ingest_text_to_vector_database(para.text, index, message_vectors)

    elif file_extension == '.txt':
        with open(file_path, 'r') as f:
            text = f.read()
            chunks = split_into_chunks(text)
            for chunk in chunks:
                ingest_text_to_vector_database(chunk, index, message_vectors)

    elif file_extension == '.pdf':
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfFileReader(f)
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                text = page.extract_text()
                ingest_text_to_vector_database(text, index, message_vectors)

    else:
        print(f"Unsupported file format: {file_extension}")

def split_into_chunks(text, chunk_size=50):
    sentences = sent_tokenize(text)
    chunks = []

    current_chunk = ""
    current_chunk_size = 0
    for sentence in sentences:
        sentence_size = len(sentence.split())

        if current_chunk_size + sentence_size > chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = ""
            current_chunk_size = 0

        current_chunk += sentence + " "
        current_chunk_size += sentence_size

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def process_json_value(value):
    if isinstance(value, str):
        return [value]
    elif isinstance(value, list):
        result = []
        for item in value:
            result.extend(process_json_value(item))
        return result
    elif isinstance(value, dict):
        result = []
        for key in value:
            result.extend(process_json_value(value[key]))
        return result
    else:
        return []

def save_embedded_file_paths(embedded_file_paths):
    with open("embedded_file_paths.pkl", "wb") as f:
        pickle.dump(embedded_file_paths, f)

def load_embedded_file_paths():
    if os.path.exists("embedded_file_paths.pkl"):
        with open("embedded_file_paths.pkl", "rb") as f:
            embedded_file_paths = pickle.load(f)
    else:
        embedded_file_paths = set()
    return embedded_file_paths

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames()
    return file_paths

def main():
    file_paths = open_file_dialog()
    embedded_file_paths = load_embedded_file_paths()

    if file_paths:
        for file_path in file_paths:
            if file_path not in embedded_file_paths:
                ingest_file(file_path)
                print("Ingested " + str(file_path))
                embedded_file_paths.add(file_path)
                save_embedded_file_paths(embedded_file_paths)
            else:
                print(f"{file_path} has already been embedded.")

if __name__ == '__main__':
    main()