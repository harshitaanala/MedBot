# utils/pdf_processor.py
import PyPDF2
import openai
import streamlit as st

openai.api_key = st.secrets["openai"]["api_key"]

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_summary(text):
    prompt = f"Summarize the following medical report for a patient in simple terms:\n\n{text}"
    response = openai.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful and friendly medical assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=700
    )
    return response['choices'][0]['message']['content']

def extract_keywords(text):
    prompt = f"Extract key medical terms, symptoms, and diagnoses from this report:\n\n{text}"
    response = openai.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a medical language expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )
    return response['choices'][0]['message']['content']

def generate_follow_up_questions(text):
    prompt = f"Based on this report, suggest follow-up questions the patient could ask the doctor:\n\n{text}"
    response = openai.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a medical assistant helping patients understand what to ask."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response['choices'][0]['message']['content']
