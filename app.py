import streamlit as st

from utils.pdf_loader import extract_text_from_pdf
from utils.voice_module import record_voice
import os

import openai
openai.api_key = openai_api_key

response = openai.Completion.create(
    model="text-davinci-003",
    prompt="Hello, world!",
    max_tokens=5
)

st.write(response.choices[0].text.strip())

openai_api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="🩺 MedBot - Doctor in a PDF")
st.title("🩺 MedBot – Understand Your Medical Report")

with st.sidebar:
    st.header("Voice Assistant")
    voice_query = record_voice()

uploaded_file = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])

if uploaded_file:
    report_text = extract_text_from_pdf(uploaded_file)
    st.success("Report successfully extracted!")

    if st.button("Get Summary"):
        chain = load_chain_from_config("configs/summary_chain.json")
        result = chain.run({"report_text": report_text})
        st.subheader("📝 Summary")
        st.write(result)

    if st.button("Extract Diagnosis & Symptoms"):
        chain = load_chain_from_config("configs/diagnosis_chain.json")
        result = chain.run({"report_text": report_text})
        st.subheader("💊 Diagnosis & Symptoms")
        st.write(result)

    if st.button("Follow-up Questions"):
        chain = load_chain_from_config("configs/followup_chain.json")
        result = chain.run({"report_text": report_text})
        st.subheader("❓ Follow-Up Questions")
        st.write(result)

if voice_query:
    st.subheader("🎙️ Your Voice Query")
    st.write(voice_query)
    if uploaded_file:
        qna_chain = load_chain_from_config("configs/summary_chain.json")
        reply = qna_chain.run({"report_text": report_text + "\n\nUser question: " + voice_query})
        st.subheader("🤖 AI Response")
        st.write(reply)
