# utils/pdf_processor.py
import PyPDF2
from openai import OpenAI


import streamlit as st
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

#openai.api_key = st.secrets["openai"]["api_key"]

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_summary(text):
    prompt = f"Summarize the following medical report for a patient in simple terms:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Ensure you're using a valid model
        messages=[
            {"role": "system", "content": "You are a helpful and friendly medical assistant."},
            {"role": "user", "content": f"Summarize the following medical report for a patient in simple terms:\n\n{text}"}
        ],
        temperature=0.5,
        max_tokens=700
    )
    return response.choices[0].message.content.strip()  # Extract the text from the response

def extract_keywords(text):
    prompt = f"Extract key medical terms, symptoms, and diagnoses from this report:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Ensure you're using a valid model
        messages=[
            {"role": "system", "content": "You are a helpful and friendly medical assistant."},
            {"role": "user", "content": f"Summarize the following medical report for a patient in simple terms:\n\n{text}"}
        ],
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()  # Extract the text from the response

def generate_follow_up_questions(text):
    prompt = f"Based on this report, suggest follow-up questions the patient could ask the doctor:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Ensure you're using a valid model
        messages=[
            {"role": "system", "content": "You are a helpful and friendly medical assistant."},
            {"role": "user", "content": f"Summarize the following medical report for a patient in simple terms:\n\n{text}"}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()  # Extract the text from the response

def chat_with_doctor_bot(user_input, context_text):
    messages = [
        {"role": "system", "content": "You are a compassionate and knowledgeable medical assistant. Help the user understand their symptoms or report content."},
        {"role": "user", "content": f"The context is: {context_text[:2000]}\n\nQuestion: {user_input}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-3.5-turbo if not available
        messages=messages,
        temperature=0.6,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def diagnose_and_recommend(symptoms_text, context_text=""):
    prompt = f"""
You are a licensed medical assistant AI. A user has described the following symptoms:\n
{symptoms_text}\n

{f"Their medical report also includes: {context_text[:2000]}" if context_text else ""}

Based on this, do the following:
1. Identify possible conditions (diagnosis) in simple terms.
2. Suggest over-the-counter medications or treatment (avoid prescription drugs).
3. Add a disclaimer that a doctor should be consulted for confirmation.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a helpful and careful AI medical assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=700
    )
    return response.choices[0].message.content.strip()

