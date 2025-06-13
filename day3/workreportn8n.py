import streamlit as st
import datetime
import pytz
import google.generativeai as genai
import os
import pandas as pd
import requests
import json

# Configure Gemini API with inbuilt API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyD7mTwA39UeYAxMsGCJlabk7u5Xi1EQTfA"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# n8n webhook URL
N8N_WEBHOOK_URL = "https://hariharan19.app.n8n.cloud/webhook-test/7c5e64ef-fb24-45ec-b47f-9b3aa6764fc1"

# Function to get current IST date
def get_ist_date():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.datetime.now(ist).strftime("%Y-%m-%d")

# Function to send data to n8n webhook
def send_to_n8n_webhook(work_title, status, team_name, email, date):
    payload = {
        "work_title": work_title,
        "status": status,
        "team_name": team_name,
        "email": email,
        "date": date
    }
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# Streamlit app
st.title("Work Report System")

# Input form for work report
with st.form(key="work_report_form"):
    work_title = st.text_input("Title of the Work")
    status = st.selectbox("Status", ["Completed", "Not Completed", "Planned"])
    team_name = st.text_input("Team Name")
    email = st.text_input("Email")
    date = get_ist_date()
    
    st.write(f"Date (IST): {date}")
    
    submit_button = st.form_submit_button(label="Submit Report")

# Initialize or load work report log
if not os.path.exists("work_report_log.csv"):
    pd.DataFrame(columns=["Work Title", "Status", "Team Name", "Email", "Date"]).to_csv("work_report_log.csv", index=False)

# Process form submission
if submit_button:
    if work_title and status and team_name and email:
        report_data = f"Work Title: {work_title}, Status: {status}, Team Name: {team_name}, Email: {email}, Date: {date}"
        try:
            # Use Gemini API to generate confirmation
            response = model.generate_content(f"Generate a confirmation message for work report submission: {report_data}")
            st.success(f"Report Submitted!\n{response.text}")
            
            # Append to CSV
            new_entry = pd.DataFrame([[work_title, status, team_name, email, date]], 
                                   columns=["Work Title", "Status", "Team Name", "Email", "Date"])
            new_entry.to_csv("work_report_log.csv", mode="a", header=False, index=False)
            
            # Send data to n8n webhook
            webhook_response, webhook_error = send_to_n8n_webhook(work_title, status, team_name, email, date)
            if webhook_error:
                st.error(f"Failed to send data to n8n webhook: {webhook_error}")
            else:
                st.info("Data successfully sent to n8n webhook!")
        except Exception as e:
            st.error(f"Error with Gemini API: {str(e)}")
    else:
        st.error("Please fill in all fields.")

# Load and display work report log
df = pd.read_csv("work_report_log.csv")
if not df.empty:
    st.subheader("Work Report Log")
    st.dataframe(df)