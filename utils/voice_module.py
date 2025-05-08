import streamlit_speech_to_text as stt

def record_voice():
    st.info("Click the mic to ask a question")
    voice_input = stt.speech_to_text()
    return voice_input
