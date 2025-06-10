import streamlit as st
import datetime
import pytz
import google.generativeai as genai
import os
import pandas as pd
import plotly.express as px

# Configure Gemini API with inbuilt API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyD7mTwA39UeYAxMsGCJlabk7u5Xi1EQTfA"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to get current IST time
def get_ist_time():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

# Function to get location (mocked; replace with geocoder/GPS API if needed)
def get_location():
    return "Campus Classroom"

# Function to calculate attendance percentage
def calculate_attendance_percentage(df, name, subject):
    if not df.empty:
        total_classes = len(df[df['Subject'] == subject])
        attended_classes = len(df[(df['Name'] == name) & (df['Subject'] == subject)])
        return (attended_classes / total_classes * 100) if total_classes > 0 else 0
    return 0

# Streamlit app
st.title("Student Attendance System")

# Input form
with st.form(key="attendance_form"):
    name = st.text_input("Student Name")
    department = st.selectbox("Department", ["Computer Science", "Mechanical", "Electrical", "Civil", "Biotechnology"])
    subject = st.text_input("Subject")
    location = get_location()
    timestamp = get_ist_time()
    
    st.write(f"Location: {location}")
    st.write(f"Time (IST): {timestamp}")
    
    submit_button = st.form_submit_button(label="Submit Attendance")

# Initialize or load attendance log
if not os.path.exists("attendance_log.csv"):
    pd.DataFrame(columns=["Name", "Department", "Subject", "Location", "Timestamp"]).to_csv("attendance_log.csv", index=False)

# Process form submission
if submit_button:
    if name and department and subject:
        attendance_data = f"Name: {name}, Department: {department}, Subject: {subject}, Location: {location}, Time: {timestamp}"
        try:
            # Use Gemini API to generate confirmation
            response = model.generate_content(f"Generate a confirmation message for student attendance: {attendance_data}")
            st.success(f"Attendance Recorded!\n{response.text}")
            
            # Append to CSV
            new_entry = pd.DataFrame([[name, department, subject, location, timestamp]], 
                                   columns=["Name", "Department", "Subject", "Location", "Timestamp"])
            new_entry.to_csv("attendance_log.csv", mode="a", header=False, index=False)
        except Exception as e:
            st.error(f"Error with Gemini API: {str(e)}")
    else:
        st.error("Please fill in all fields.")

# Load attendance data
df = pd.read_csv("attendance_log.csv")

# Display attendance log
if not df.empty:
    st.subheader("Attendance Log")
    st.dataframe(df)

    # Graphical representation of attendance percentage
    st.subheader("Attendance Percentage")
    selected_student = st.selectbox("Select Student for Attendance Graph", df["Name"].unique())
    selected_subject = st.selectbox("Select Subject for Attendance Graph", df["Subject"].unique())
    
    attendance_percentage = calculate_attendance_percentage(df, selected_student, selected_subject)
    
    # Plot attendance percentage
    fig = px.pie(values=[attendance_percentage, 100 - attendance_percentage], 
                 names=["Attended", "Missed"], 
                 title=f"Attendance for {selected_student} in {selected_subject} ({attendance_percentage:.2f}%)")
    st.plotly_chart(fig)
    
    # Maximum attendance percentage to attain per semester
    st.subheader("Attendance Goal")
    max_attendance_goal = 75.0  # Example: 75% is the minimum required attendance
    st.write(f"Maximum Attendance Goal per Semester for {selected_subject}: **{max_attendance_goal}%**")
    if attendance_percentage >= max_attendance_goal:
        st.success(f"Congratulations! {selected_student} has achieved {attendance_percentage:.2f}% attendance in {selected_subject}, meeting or exceeding the {max_attendance_goal}% goal.")
    else:
        st.warning(f"{selected_student} has {attendance_percentage:.2f}% attendance in {selected_subject}. Need {(max_attendance_goal - attendance_percentage):.2f}% more to meet the {max_attendance_goal}% goal.")