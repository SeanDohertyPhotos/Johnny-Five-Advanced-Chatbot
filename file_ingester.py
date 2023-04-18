import json
import os
import tkinter as tk
from tkinter import filedialog

import docx
import pandas as pd
import PyPDF2
from bs4 import BeautifulSoup

from main import get_index_and_message_vectors, ingest_text_to_vector_database

index, message_vectors = get_index_and_message_vectors()

def ingest_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == '.json':
        with open(file_path, 'r') as f:
            data = json.load(f)
            for item in data:
                for key in item:
                    ingest_text_to_vector_database(item[key], index, message_vectors)

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
            ingest_text_to_vector_database(text, index, message_vectors)

    elif file_extension == '.pdf':
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfFileReader(f)
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                text = page.extract_text()
                ingest_text_to_vector_database(text, index, message_vectors)

    else:
        print(f"Unsupported file format: {file_extension}")


def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path


def main():
    file_path = open_file_dialog()
    if file_path:
        ingest_file(file_path)
        print("Ingested" + str(file_path))


if __name__ == '__main__':
    main()
