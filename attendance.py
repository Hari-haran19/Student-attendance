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

# Initialize or load attendance and marks data
if not os.path.exists("attendance_log.csv"):
    pd.DataFrame(columns=["Name", "Department", "Subject", "Location", "Timestamp"]).to_csv("attendance_log.csv", index=False)
if not os.path.exists("marks_log.csv"):
    pd.DataFrame(columns=["Name", "Subject", "Marks"]).to_csv("marks_log.csv", index=False)
if not os.path.exists("achievements_log.csv"):
    pd.DataFrame(columns=["Name", "Achievement"]).to_csv("achievements_log.csv", index=False)

# Streamlit app
st.title("Student Attendance System")

# Sidebar for additional features
st.sidebar.title("Student Dashboard")
sidebar_option = st.sidebar.selectbox("Select Option", ["Check Attendance Percentage", "View Subject Marks", "Update Achievements"])

# Main form for attendance
with st.form(key="attendance_form"):
    name = st.text_input("Student Name")
    department = st.selectbox("Department", ["Computer Science", "Mechanical", "Electrical", "Civil", "Biotechnology"])
    subject = st.text_input("Subject")
    location = get_location()
    timestamp = get_ist_time()
    
    st.write(f"Location: {location}")
    st.write(f"Time (IST): {timestamp}")
    
    submit_button = st.form_submit_button(label="Submit Attendance")

# Process attendance submission
if submit_button:
    if name and department and subject:
        attendance_data = f"Name: {name}, Department: {department}, Subject: {subject}, Location: {location}, Time: {timestamp}"
        try:
            response = model.generate_content(f"Generate a confirmation message for student attendance: {attendance_data}")
            st.success(f"Attendance Recorded!\n{response.text}")
            
            new_entry = pd.DataFrame([[name, department, subject, location, timestamp]], 
                                   columns=["Name", "Department", "Subject", "Location", "Timestamp"])
            new_entry.to_csv("attendance_log.csv", mode="a", header=False, index=False)
        except Exception as e:
            st.error(f"Error with Gemini API: {str(e)}")
    else:
        st.error("Please fill in all fields.")

# Load data
df_attendance = pd.read_csv("attendance_log.csv")
df_marks = pd.read_csv("marks_log.csv")
df_achievements = pd.read_csv("achievements_log.csv")

# Sidebar functionalities
if sidebar_option == "Check Attendance Percentage":
    st.sidebar.subheader("Attendance Percentage")
    selected_student = st.sidebar.selectbox("Select Student", df_attendance["Name"].unique(), key="attendance_student")
    selected_subject = st.sidebar.selectbox("Select Subject", df_attendance["Subject"].unique(), key="attendance_subject")
    
    attendance_percentage = calculate_attendance_percentage(df_attendance, selected_student, selected_subject)
    st.sidebar.write(f"Attendance for {selected_subject}: {attendance_percentage:.2f}%")
    
    # Plot attendance percentage
    fig = px.pie(values=[attendance_percentage, 100 - attendance_percentage], 
                 names=["Attended", "Missed"], 
                 title=f"Attendance for {selected_student} in {selected_subject}")
    st.sidebar.plotly_chart(fig, use_container_width=True)

elif sidebar_option == "View Subject Marks":
    st.sidebar.subheader("Subject Marks")
    selected_student = st.sidebar.selectbox("Select Student", df_marks["Name"].unique(), key="marks_student")
    selected_subject = st.sidebar.selectbox("Select Subject", df_marks["Subject"].unique(), key="marks_subject")
    
    student_marks = df_marks[(df_marks["Name"] == selected_student) & (df_marks["Subject"] == selected_subject)]
    if not student_marks.empty:
        marks = student_marks["Marks"].iloc[0]
        st.sidebar.write(f"Marks for {selected_subject}: {marks}")
    else:
        st.sidebar.write("No marks recorded for this student and subject.")
    
    # Form to add/update marks
    with st.sidebar.form(key="marks_form"):
        new_marks = st.number_input("Enter Marks (0-100)", min_value=0, max_value=100, step=1)
        submit_marks = st.form_submit_button("Submit Marks")
        if submit_marks:
            new_marks_entry = pd.DataFrame([[selected_student, selected_subject, new_marks]], 
                                         columns=["Name", "Subject", "Marks"])
            df_marks = df_marks[~((df_marks["Name"] == selected_student) & (df_marks["Subject"] == selected_subject))]
            df_marks = pd.concat([df_marks, new_marks_entry], ignore_index=True)
            df_marks.to_csv("marks_log.csv", index=False)
            st.sidebar.success(f"Marks updated for {selected_student} in {selected_subject}: {new_marks}")

elif sidebar_option == "Update Achievements":
    st.sidebar.subheader("Update Achievements")
    selected_student = st.sidebar.selectbox("Select Student", df_attendance["Name"].unique(), key="achievements_student")
    achievement = st.sidebar.text_input("Enter Achievement")
    
    with st.sidebar.form(key="achievements_form"):
        submit_achievement = st.form_submit_button("Submit Achievement")
        if submit_achievement and achievement:
            try:
                response = model.generate_content(f"Generate a congratulatory message for student {selected_student} for achievement: {achievement}")
                st.sidebar.success(f"Achievement Recorded!\n{response.text}")
                
                new_achievement = pd.DataFrame([[selected_student, achievement]], columns=["Name", "Achievement"])
                new_achievement.to_csv("achievements_log.csv", mode="a", header=False, index=False)
            except Exception as e:
                st.sidebar.error(f"Error with Gemini API: {str(e)}")
    
    # Display achievements
    student_achievements = df_achievements[df_achievements["Name"] == selected_student]
    if not student_achievements.empty:
        st.sidebar.subheader(f"Achievements for {selected_student}")
        st.sidebar.write(student_achievements["Achievement"].tolist())

# Display attendance log in main section
if not df_attendance.empty:
    st.subheader("Attendance Log")
    st.dataframe(df_attendance)