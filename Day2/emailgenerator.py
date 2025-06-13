import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os

# 🔐 INBUILT API KEY Setup
GEMINI_API_KEY = "AIzaSyD7mTwA39UeYAxMsGCJlabk7u5Xi1EQTfA"
genai.configure(api_key=GEMINI_API_KEY)

# 🌟 Initialize Model
model = genai.GenerativeModel('gemini-2.0-flash')

st.title("✉️ AI Email Generator")
st.markdown("Easily generate emails with your input, desired tone, and format using Gemini AI.")

# 📥 User Input
user_input = st.text_area("Enter your text or context for the email:")

# 🎛️ Tone & Format Options
col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Select Tone", ["Professional", "Friendly", "Persuasive", "Appreciative", "Empathetic"])
with col2:
    email_type = st.selectbox("Select Email Format", ["Formal", "Informal", "Follow-up", "Apology", "Request"])

# 🧠 Generate Email Function
def generate_email(prompt, tone, format_type):
    full_prompt = f"""Write an email based on the following input:
    - Input: {prompt}
    - Format: {format_type}
    - Tone: {tone}
    """
    response = model.generate_content(full_prompt)
    return response.text

# 📧 Email Output
if st.button("Generate Email"):
    if user_input.strip():
        generated_email = generate_email(user_input, tone, email_type)
        st.session_state['generated_email'] = generated_email
    else:
        st.warning("Please enter some text to generate an email.")

# 🔁 Regenerate Option
if st.button("Regenerate with New Tone/Format"):
    if user_input.strip():
        generated_email = generate_email(user_input, tone, email_type)
        st.session_state['generated_email'] = generated_email
    else:
        st.warning("Please enter input text before regenerating.")

# 📄 Show Output
if 'generated_email' in st.session_state:
    st.subheader("📨 Generated Email")
    st.text_area("Generated Email", st.session_state['generated_email'], height=300)

    # 📥 Download PDF Function
    def create_pdf(text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)
        file_path = "/tmp/generated_email.pdf"
        pdf.output(file_path)
        return file_path

    # 📥 Download Button
    pdf_path = create_pdf
