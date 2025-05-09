import streamlit as st
from utils.pdf_processor import (
    extract_text_from_pdf,
    generate_summary,
    extract_keywords,
    generate_follow_up_questions
)

st.set_page_config(page_title="🩺 MedBot - Doctor in a PDF", layout="centered")
st.title("🩺 MedBot")
st.subheader("Doctor in a PDF: Simplify Your Medical Reports")

uploaded_file = st.file_uploader("📄 Upload your medical report (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    if st.button("🧠 Generate Summary"):
        with st.spinner("Generating patient-friendly summary..."):
            summary = generate_summary(text)
            st.subheader("📋 Summary")
            st.write(summary)
            st.download_button("⬇️ Export Summary", summary, file_name="summary.txt")

    if st.button("🔑 Extract Keywords"):
        with st.spinner("Extracting key medical terms..."):
            keywords = extract_keywords(text)
            st.subheader("🔍 Medical Keywords")
            st.write(keywords)

    if st.button("❓ Follow-up Questions"):
        with st.spinner("Generating questions for doctor visit..."):
            questions = generate_follow_up_questions(text)
            st.subheader("💬 Suggested Follow-Up Questions")
            st.write(questions)
