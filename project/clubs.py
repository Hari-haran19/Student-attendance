# -------------------------------
# 🔗 Set your n8n webhook URL here
WEBHOOK_URL = "https://hari1907.app.n8n.cloud/webhook-test/e13feee5-3213-44aa-b56c-0110fc03731c"
# -------------------------------

import streamlit as st
import requests

st.set_page_config(page_title="🎓 Student-Club Matcher", page_icon="🤖")
st.title("🎯 Student to Club/Event Matcher")

st.markdown("Fill in your details and get matched to the perfect club or event based on your interests!")

# --- Form for Student Data ---
with st.form("student_form"):
    name = st.text_input("Full Name", placeholder="John Doe")
    number = st.text_input("Phone Number", placeholder="9876543210")
    email = st.text_input("Email Address", placeholder="john@example.com")
    department = st.text_input("Department", placeholder="Computer Science")

    interests = st.text_area("Interests", placeholder="e.g. AI, Robotics, Music")
    hobbies = st.text_area("Hobbies", placeholder="e.g. Reading, Gaming")

    profile_link = st.text_input("LinkedIn/Instagram Profile", placeholder="https://linkedin.com/in/johndoe")

    submitted = st.form_submit_button("Submit")

# --- Handle Form Submission ---
if submitted:
    if not name or not email or not interests:
        st.warning("Please fill in all required fields: Name, Email, Interests.")
    else:
        payload = {
            "name": name.strip(),
            "number": number.strip(),
            "email": email.strip(),
            "department": department.strip(),
            "interests": interests.strip(),
            "hobbies": hobbies.strip(),
            "profile_link": profile_link.strip()
        }

        try:
            response = requests.post(WEBHOOK_URL, json=payload)

            if response.status_code == 200:
                st.success("✅ Your data has been submitted successfully! You’ll receive event recommendations soon.")
            else:
                st.error(f"❌ Submission failed with status code {response.status_code}")
                st.text(f"Response: {response.text}")
        except Exception as e:
            st.error("⚠️ Failed to connect to the webhook.")
            st.exception(e)
