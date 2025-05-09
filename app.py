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

# ✅ Must be the very first Streamlit command
st.set_page_config(page_title="🩺 MedBot - Doctor in a PDF", layout="centered")

st.title("🩺 MedBot")
st.subheader("Doctor in a PDF: Simplify Your Medical Reports")

uploaded_file = st.file_uploader("📄 Upload your medical report (PDF)", type=["pdf"])
text = ""

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
            reply = chat_with_doctor_bot(prompt, text)
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
            diagnosis = diagnose_and_recommend(symptom_input, text if uploaded_file else "")
            st.subheader("🩺 Possible Diagnosis")
            st.markdown(diagnosis)


# ================================
# 🏥 Nearby Hospital Finder
# ================================
st.markdown("---")
st.subheader("🏥 Nearby Hospitals")

with st.expander("📍 Find hospitals within 5km based on your location"):
    location_input = st.text_input("Enter your location (e.g., Mumbai, Andheri East or ZIP code)")

    if st.button("🔎 Search Nearby Hospitals"):
        if not location_input.strip():
            st.warning("Please enter your location.")
        else:
            with st.spinner("Searching for nearby hospitals..."):
                geolocator = Nominatim(user_agent="medbot_app")
                location = geolocator.geocode(location_input)

                if location:
                    lat, lon = location.latitude, location.longitude
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

                    hospitals = sorted(hospitals, key=lambda x: x[3])[:3]  # Top 3 nearest

                    if hospitals:
                        for idx, (name, h_lat, h_lon, dist) in enumerate(hospitals, 1):
                            st.markdown(f"**{idx}. {name}** – {dist:.2f} km away")
                            map_link = f"https://www.google.com/maps/search/?api=1&query={h_lat},{h_lon}"
                            st.markdown(f"[🗺️ View on Google Maps]({map_link})")
                    else:
                        st.warning("No hospitals found within 5km of this location.")
                else:
                    st.error("Could not find the location. Please enter a valid city or area.")

