import streamlit as st
import requests
from utils.pdf_processor import (
    extract_text_from_pdf,
    generate_summary,
    extract_keywords,
    generate_follow_up_questions,
    chat_with_doctor_bot,
    diagnose_and_recommend
)

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import openai
import tempfile
import os
import time
import base64

# ✅ Set API key from Streamlit secrets
openai.api_key = st.secrets["api_key"]

# ✅ Set Streamlit config
st.set_page_config(page_title="🩺 MedBot - Doctor in a PDF", layout="centered")

st.title("🩺 MedBot")
st.subheader("Doctor in a PDF: Simplify Your Medical Reports")

# ================================
# 📄 PDF Upload
# ================================
uploaded_files = st.file_uploader("📄 Upload your medical reports (PDF)", type=["pdf"], accept_multiple_files=True)

combined_text = ""
all_texts = []

if uploaded_files:
    st.write("✅ Uploaded Reports:")
    for file in uploaded_files:
        st.markdown(f"- {file.name}")
        with st.spinner(f"Extracting text from {file.name}..."):
            text = extract_text_from_pdf(file)
            all_texts.append(text)

    combined_text = "\n\n".join(all_texts)

    if st.button("🧠 Generate Summary"):
        with st.spinner("Generating patient-friendly summary..."):
            summary = generate_summary(combined_text)
            st.subheader("📋 Summary")
            st.write(summary)
            st.download_button("⬇️ Export Summary", summary, file_name="summary.txt")

    if st.button("🔑 Extract Keywords"):
        with st.spinner("Extracting key medical terms..."):
            keywords = extract_keywords(combined_text)
            st.subheader("🔍 Medical Keywords")
            st.write(keywords)

    if st.button("❓ Follow-up Questions"):
        with st.spinner("Generating questions for doctor visit..."):
            questions = generate_follow_up_questions(combined_text)
            st.subheader("💬 Suggested Follow-Up Questions")
            st.write(questions)

# ================================
# 🤖 Chatbot (Sidebar)
# ================================
st.sidebar.markdown("### 🤖 Ask MedBot")
st.sidebar.markdown("Ask any health-related doubts or questions about your medical report.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.sidebar.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.sidebar.chat_input("Type your question here..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.sidebar.chat_message("user"):
        st.markdown(prompt)

    with st.sidebar.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat_with_doctor_bot(prompt, combined_text)
            st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# ================================
# 💊 Symptom Checker
# ================================
st.markdown("---")
st.subheader("💊 Symptom Checker & Medicine Suggestions")
symptom_input = st.text_area("📝 Describe your symptoms")

if st.button("🔍 Diagnose & Recommend Medicines"):
    if not symptom_input.strip():
        st.warning("Please describe your symptoms.")
    else:
        with st.spinner("Analyzing symptoms..."):
            diagnosis = diagnose_and_recommend(symptom_input, combined_text if uploaded_files else "")
            st.subheader("🩺 Possible Diagnosis")
            st.markdown(diagnosis)

# ================================
# 🏥 Smart Hospital Finder
# ================================
st.markdown("---")
st.subheader("🏥 Smart Hospital Finder Based on Symptoms")

with st.expander("📍 Get specialized hospitals nearby based on your symptoms"):
    location_input = st.text_input("Enter your location (e.g., Mumbai, Andheri East, or ZIP code)")

    if st.button("📡 Recommend Nearby Hospitals"):
        if not symptom_input.strip():
            st.warning("Please enter your symptoms above before searching.")
        elif not location_input.strip():
            st.warning("Please enter your location.")
        else:
            with st.spinner("Analyzing symptoms and searching hospitals..."):

                def determine_hospital_type(symptoms):
                    symptoms = symptoms.lower()
                    if any(word in symptoms for word in ["eye", "vision", "blur", "sight"]):
                        return "eye"
                    elif any(word in symptoms for word in ["heart", "chest pain", "cardiac", "palpitation"]):
                        return "cardiology"
                    elif any(word in symptoms for word in ["skin", "rash", "itching", "eczema", "acne"]):
                        return "dermatology"
                    elif any(word in symptoms for word in ["bones", "joint", "orthopedic", "fracture", "back pain"]):
                        return "orthopedic"
                    elif any(word in symptoms for word in ["fever", "cold", "cough", "flu", "body pain"]):
                        return "general"
                    else:
                        return "general"

                hospital_type = determine_hospital_type(symptom_input)

                geolocator = Nominatim(user_agent="medbot_app")
                location = geolocator.geocode(location_input)

                if location:
                    lat, lon = location.latitude, location.longitude

                    keyword_map = {
                        "general": '"amenity"="hospital"',
                        "eye": '"name"~"Eye|Ophthalmology"',
                        "cardiology": '"name"~"Cardiology|Heart"',
                        "dermatology": '"name"~"Skin|Dermatology"',
                        "orthopedic": '"name"~"Ortho|Orthopedic"'
                    }
                    filter_tag = keyword_map.get(hospital_type, '"amenity"="hospital"')

                    overpass_url = "http://overpass-api.de/api/interpreter"
                    query = f"""
                    [out:json];
                    (
                      node[{filter_tag}](around:10000,{lat},{lon});
                      way[{filter_tag}](around:10000,{lat},{lon});
                      relation[{filter_tag}](around:10000,{lat},{lon});
                    );
                    out center;
                    """
                    response = requests.post(overpass_url, data={'data': query})
                    data = response.json()

                    hospitals = []
                    for element in data['elements']:
                        if 'tags' in element and 'name' in element['tags']:
                            name = element['tags']['name']
                            if 'lat' in element:
                                h_lat, h_lon = element['lat'], element['lon']
                            else:
                                h_lat, h_lon = element['center']['lat'], element['center']['lon']
                            distance = geodesic((lat, lon), (h_lat, h_lon)).km
                            hospitals.append((name, h_lat, h_lon, distance))

                    hospitals = [h for h in hospitals if h[3] <= 10]
                    hospitals = sorted(hospitals, key=lambda x: x[3])[:3]

                    st.markdown(f"### 🏥 Top {hospital_type.capitalize()} Hospitals Near You")
                    if hospitals:
                        for idx, (name, h_lat, h_lon, dist) in enumerate(hospitals, 1):
                            st.markdown(f"**{idx}. {name}** – {dist:.2f} km away")
                            map_link = f"https://www.google.com/maps/search/?api=1&query={h_lat},{h_lon}"
                            st.markdown(f"[🗺️ View on Google Maps]({map_link})")
                    else:
                        st.warning(f"No {hospital_type} hospitals found within 10 km of your location.")
                else:
                    st.error("Could not find your location. Please enter a valid area or ZIP code.")
