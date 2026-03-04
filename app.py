import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


# --- INITIAL SETUP ---
st.set_page_config(page_title="Auto-RFP", page_icon="🏦", layout="wide")
st.title("🏦 Auto-RFP: Intelligent Lifecycle Management")

# Setup Gemini (You'll need to input your API key in the UI)
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- SIDEBAR: UPLOAD & SUMMARY ---
st.sidebar.header("Upload RFP Document")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file and api_key:
    # Read PDF
    reader = PdfReader(uploaded_file)
    raw_text = "".join([page.extract_text() for page in reader.pages])
    
    st.sidebar.success("RFP Loaded!")
    
    # Milestone 1: Automated Summary (Sidebar)
    if st.sidebar.button("Generate Executive Summary"):
        with st.spinner("Analyzing..."):
            prompt = f"Summarize this RFP. Extract: 1. Deadline, 2. EMD Amount, 3. Eligibility. Text: {raw_text[:10000]}"
            response = model.generate_content(prompt)
            st.sidebar.write(response.text)

# --- MAIN AREA: MILESTONES ---
tab1, tab2, tab3 = st.tabs(["Drafting", "Query Assistant", "Corrigendum"])

with tab1:
    st.header("Draft New RFP Sections")
    context = st.text_area("What is this RFP for? (e.g., 'ATM Maintenance for Chennai')")
    if st.button("Generate Draft"):
        prompt = f"Write a professional banking RFP section for: {context}"
        draft = model.generate_content(prompt)
        st.write(draft.text)

with tab2:
    st.header("RFP Query Bot")
    user_query = st.text_input("Ask anything about the uploaded RFP:")
    if user_query and uploaded_file:
        # Simple RAG-style vibe
        prompt = f"Based on this RFP text: {raw_text[:20000]}, answer this: {user_query}"
        answer = model.generate_content(prompt)
        st.chat_message("assistant").write(answer.text)

with tab3:
    st.header("Generate Corrigendum")
    change = st.text_input("What change is being made? (e.g., 'Extend date to Dec 1st')")
    if st.button("Create Corrigendum"):
        prompt = f"Draft a formal bank corrigendum notice for this change: {change}. Use official banking language."
        corrigendum = model.generate_content(prompt)
        st.info(corrigendum.text)