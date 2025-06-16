import streamlit as st
import requests

# -------------------------------
# 🔗 Configure your n8n webhook URL here
WEBHOOK_URL = "https://hariharan19.app.n8n.cloud/webhook-test/48601122-18b0-4a92-bf2c-2e730ba35a59"
# -------------------------------

st.set_page_config(page_title="Student-Club Matcher", page_icon="🎯")
st.title("🎯 Student-Club Matcher Form")

st.markdown("Fill out the form below to get matched with relevant clubs and events based on your interests!")

# --- Streamlit Form ---
with st.form("student_form"):
    name = st.text_input("Name", placeholder="Enter your full name")
    email = st.text_input("Email", placeholder="Enter your email")
    interests = st.text_area("Interests", placeholder="E.g. robotics, music, ai, photography")
    
    submitted = st.form_submit_button("Submit")

# --- Handle Form Submission ---
if submitted:
    if not name or not email or not interests:
        st.warning("Please fill in all fields before submitting.")
    else:
        # Prepare JSON payload
        payload = {
            "name": name.strip(),
            "email": email.strip(),
            "interests": interests.strip()
        }

        try:
            # Send POST request to n8n webhook
            response = requests.post(WEBHOOK_URL, json=payload)

            if response.status_code == 200:
                st.success("✅ Your data has been submitted successfully! You'll receive recommendations soon.")
            else:
                st.error(f"❌ Submission failed. Server responded with status code {response.status_code}")
                st.text(f"Response: {response.text}")
        except Exception as e:
            st.error("⚠️ Failed to connect to the webhook. Please check your internet or webhook URL.")
            st.exception(e)
