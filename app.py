import streamlit as st
from langchain_mcp.loader import load_chain_from_config
from utils.pdf_loader import extract_text_from_pdf

import os
import utils.voice_module as voice

from utils.voice_module import record_and_transcribe

st.set_page_config(page_title="MedBot Voice Chat", layout="centered")
st.title("🩺 MedBot - Doctor in a PDF")
st.subheader("🎤 Talk to MedBot using your voice")

if st.button("🎙 Start Voice Chat"):
    transcribed = record_and_transcribe()
    if transcribed:
        st.write("🗣️ You said:", transcribed)

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
