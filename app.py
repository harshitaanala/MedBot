import streamlit as st

st.set_page_config(page_title="🗺️ Nearby Hospitals", layout="centered")

from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import requests
from utils.pdf_processor import (
    extract_text_from_pdf,
    generate_summary,
    extract_keywords,
    generate_follow_up_questions,
    chat_with_doctor_bot,
    diagnose_and_recommend  # Add this function in pdf_processor.py
)
from openai import OpenAI

# Set up the Streamlit page



st.title("🏥 Find Nearby Hospitals")
st.markdown("We'll detect your location and suggest the **top 3 hospitals** within 5 km.")

# 1. Get user location using Nominatim or manual input
geolocator = Nominatim(user_agent="medbot-hospitals")

location_input = st.text_input("Enter your location or area (e.g., Andheri East, Mumbai):")

if location_input:
    location = geolocator.geocode(location_input)
    
    if location:
        lat, lon = location.latitude, location.longitude
        st.success(f"📍 Location detected: {location.address}")

        # 2. Use OpenStreetMap Overpass API to fetch hospitals
        st.info("Fetching nearby hospitals...")

        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:5000,{lat},{lon});
          way["amenity"="hospital"](around:5000,{lat},{lon});
          relation["amenity"="hospital"](around:5000,{lat},{lon});
        );
        out center;
        """

        response = requests.get(overpass_url, params={'data': query})
        data = response.json()

        hospitals = []
        for element in data['elements']:
            if 'tags' in element and 'name' in element['tags']:
                name = element['tags']['name']
                lat = element.get('lat') or element['center']['lat']
                lon = element.get('lon') or element['center']['lon']
                hospitals.append((name, lat, lon))

        # 3. Display top 3 hospitals on map
        if hospitals:
            st.success(f"✅ Found {len(hospitals)} hospitals. Showing top 3:")
            top_3 = hospitals[:3]

            # Create Map
            map_ = folium.Map(location=[location.latitude, location.longitude], zoom_start=14)
            folium.Marker(
                [location.latitude, location.longitude],
                tooltip="You are here",
                icon=folium.Icon(color='blue')
            ).add_to(map_)

            for name, lat_, lon_ in top_3:
                folium.Marker(
                    [lat_, lon_],
                    tooltip=name,
                    icon=folium.Icon(color='red', icon='plus-sign')
                ).add_to(map_)

            st_folium(map_, width=700, height=500)
        else:
            st.warning("❗ No hospitals found within 5 km.")

    else:
        st.error("Could not detect location. Try entering a more specific area.")

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

st.sidebar.markdown("### 🤖 Ask MedBot")
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

st.markdown("---")
st.subheader("💊 Symptom Checker & Medicine Suggestions")
st.markdown("Enter your symptoms below. MedBot will try to identify the condition and suggest common medications. Always consult a real doctor before taking any medicines.")

symptom_input = st.text_area("📝 Describe your symptoms")

if st.button("🔍 Diagnose & Recommend Medicines"):
    if not symptom_input.strip():
        st.warning("Please describe your symptoms.")
    else:
        with st.spinner("Analyzing symptoms..."):
            diagnosis = diagnose_and_recommend(symptom_input, text if uploaded_file else "")
            st.subheader("🩺 Possible Diagnosis")
            st.markdown(diagnosis)



