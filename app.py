import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv
from fpdf import FPDF

# --- 1. HELPERS & CONFIG ---
load_dotenv()

def create_pdf(text_content):
    """Turns text into a bytes object for download."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # latin-1 encoding helps avoid errors with standard text
    pdf.multi_cell(0, 10, txt=text_content.encode('latin-1', 'replace').decode('latin-1')) 
    return pdf.output(dest='S')

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Auto-RFP", page_icon="🏦", layout="wide")
st.title("🏦 Auto-RFP: Intelligent Lifecycle Management")

# --- 3. API KEY LOGIC ---
# First, try to get it from .env
env_key = os.getenv("GEMINI_API_KEY")

# Create a sidebar input that defaults to the .env key if it exists
api_key = st.sidebar.text_input("Gemini API Key", value=env_key if env_key else "", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
    st.stop() # Stops the app here until a key is provided

# --- 4. SIDEBAR: UPLOAD & SUMMARY ---
st.sidebar.header("Upload RFP Document")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

raw_text = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    raw_text = "".join([page.extract_text() for page in reader.pages])
    st.sidebar.success("RFP Loaded!")
    
    if st.sidebar.button("Generate Executive Summary"):
        with st.spinner("Analyzing..."):
            prompt = f"Summarize this RFP. Extract: 1. Deadline, 2. EMD Amount, 3. Eligibility. Text: {raw_text[:10000]}"
            response = model.generate_content(prompt)
            st.sidebar.markdown(response.text)

# --- 5. MAIN AREA: THE TABS ---
tab1, tab2, tab3 = st.tabs(["📄 Drafting", "🤖 Query Assistant", "✍️ Corrigendum"])

with tab1:
    st.header("Draft New RFP Sections")
    context = st.text_area("What is this RFP for? (e.g., 'ATM Maintenance for Chennai')")
    if st.button("Generate Draft", key="draft_btn"):
        with st.spinner("Drafting..."):
            prompt = f"Write a professional banking RFP section for: {context}"
            draft = model.generate_content(prompt)
            st.write(draft.text)
            
            # Download option for the draft
            pdf_bytes = create_pdf(draft.text)
            st.download_button("Download Draft as PDF", data=pdf_bytes, file_name="rfp_draft.pdf")

with tab2:
    st.header("RFP Query Bot")
    user_query = st.text_input("Ask anything about the uploaded RFP:")
    if user_query:
        if not raw_text:
            st.error("Please upload an RFP PDF in the sidebar first!")
        else:
            with st.spinner("Searching..."):
                prompt = f"Based on this RFP text: {raw_text[:20000]}, answer this: {user_query}"
                answer = model.generate_content(prompt)
                st.chat_message("assistant").write(answer.text)

with tab3:
    st.header("Generate Corrigendum")
    change = st.text_input("What change is being made? (e.g., 'Extend date to Dec 1st')")
    if st.button("Create Corrigendum", key="corr_btn"):
        with st.spinner("Generating..."):
            prompt = f"Draft a formal bank corrigendum notice for: {change}. Use official banking language."
            corrigendum = model.generate_content(prompt)
            st.info(corrigendum.text)
            
            # Download option for corrigendum
            pdf_bytes = create_pdf(corrigendum.text)
            st.download_button("Download Corrigendum as PDF", data=pdf_bytes, file_name="corrigendum.pdf")