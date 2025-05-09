# app.py
import streamlit as st
from utils.pdf_processor import (
    extract_text_from_pdf,
    generate_summary,
    extract_keywords,
    generate_follow_up_questions,
    translate_summary,
    generate_chat_response,
    check_symptoms,
    recommend_specialist
)
import base64

st.set_page_config(page_title="🩺 MedBot - Doctor in a PDF", layout="wide")
st.title("🩺 MedBot")
st.subheader("Doctor in a PDF: Simplify Your Medical Reports")

# Sidebar Chatbot UI
def chatbot_ui():
    with st.sidebar:
        st.image("assets/doctor_icon.png", width=60)
        st.markdown("### Ask MedBot")
        user_question = st.text_input("Ask a medical question")
        if user_question:
            with st.spinner("MedBot is thinking..."):
                response = generate_chat_response(user_question)
            st.markdown("**Response:**")
            st.write(response)

chatbot_ui()

# Main Area
uploaded_files = st.file_uploader("📄 Upload your medical report(s) (PDF)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    full_text = ""
    for uploaded_file in uploaded_files:
        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            full_text += extract_text_from_pdf(uploaded_file) + "\n"

    if st.button("🧠 Generate Summary"):
        with st.spinner("Generating patient-friendly summary..."):
            summary = generate_summary(full_text)
            st.subheader("📋 Summary")
            st.write(summary)
            st.download_button("⬇️ Export Summary", summary, file_name="summary.txt")

    if st.button("🌍 Translate Summary to Hindi"):
        with st.spinner("Translating to Hindi..."):
            translated = translate_summary(full_text, target_language="hi")
            st.subheader("📘 Hindi Summary")
            st.write(translated)

    if st.button("🔑 Extract Keywords"):
        with st.spinner("Extracting key medical terms..."):
            keywords = extract_keywords(full_text)
            st.subheader("🔍 Medical Keywords")
            st.write(keywords)

    if st.button("❓ Follow-up Questions"):
        with st.spinner("Generating questions for doctor visit..."):
            questions = generate_follow_up_questions(full_text)
            st.subheader("💬 Suggested Follow-Up Questions")
            st.write(questions)

    if st.button("🧾 Check Symptoms"):
        with st.spinner("Analyzing symptoms from the report..."):
            symptoms = check_symptoms(full_text)
            st.subheader("📌 Possible Symptoms")
            st.write(symptoms)

    if st.button("👨‍⚕️ Recommend Specialist"):
        with st.spinner("Identifying relevant specialist..."):
            specialist = recommend_specialist(full_text)
            st.subheader("🏥 Suggested Specialist")
            st.write(specialist)

st.markdown("---")
st.caption("Built with Langflow")
