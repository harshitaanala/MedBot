import streamlit as st
from utils.pdf_processor import (
    extract_text_from_pdf,
    generate_summary,
    extract_keywords,
    generate_follow_up_questions,
    chat_with_doctor_bot  # Add this function in pdf_processor.py
)
from openai import OpenAI

# Set up the Streamlit page
st.set_page_config(page_title="🩺 MedBot - Doctor in a PDF", layout="centered")
st.title("🩺 MedBot")
st.subheader("Doctor in a PDF: Simplify Your Medical Reports")

# File uploader
uploaded_file = st.file_uploader("📄 Upload your medical report (PDF)", type=["pdf"])

# Extracted text holder
text = ""

# Display extracted content and features
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

# =======================
# 🤖 Chatbot (Sidebar)
# =======================

st.sidebar.markdown("### 🤖 Ask MedBot (Chat)")
st.sidebar.markdown("Ask any health-related doubts or questions about your medical report.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.sidebar.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.sidebar.chat_input("Type your question here..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.sidebar.chat_message("user"):
        st.markdown(prompt)

    with st.sidebar.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat_with_doctor_bot(prompt, text)  # Use extracted text context
            st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
