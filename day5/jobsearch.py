import streamlit as st
import os
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

from duckduckgo_search import DDGS  # ✅ Only import DDGS, not DuckDuckGoSearchException

# --- Set Gemini API Key ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyAm9qlkOPZidQy2bRfQatyvgCgQokINyXM"

# --- Streamlit UI ---
st.title("📄 Resume-Powered Job Search Assistant")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # --- Load and Split Resume ---
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(pages)

    # --- Create Embeddings and Vector Store ---
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(texts, embeddings)

    # --- Create QA Chain ---
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
        retriever=vectorstore.as_retriever()
    )

    # --- Extract Keywords from Resume ---
    query = "Extract the top 5 job titles or roles suited for this resume"
    response = qa_chain.run(query)

    st.subheader("🔍 Suggested Job Titles Based on Resume")
    st.write(response)

    # --- Perform Job Search using DuckDuckGo ---
    st.subheader("📡 Real-Time Job Search")
    st.write("Searching for jobs matching your resume...")

    try:
        hiring_query = response + " jobs in India"

        with DDGS() as ddgs:
            results = ddgs.text(hiring_query, max_results=5, region="in-en")
            for r in results:
                st.write("🔗", r["title"])
                st.write(r["href"])
                st.write("---")

    except Exception as e:
        st.error(f"Error during DuckDuckGo job search: {e}")
