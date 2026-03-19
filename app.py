import streamlit as st
from google import genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv
from fpdf import FPDF
import re

# --- 1. CONFIG & SYSTEM PROMPT ---
load_dotenv()
SYSTEM_PROMPT = """You are an expert Banking Procurement Officer at Indian Bank. 
Use formal, legally-compliant language. Always refer to banking standards and DFS/IBA guidelines.
If generating a table, use Markdown format."""

# --- 2. HELPERS ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Fix for Latin-1/Rupee crash and smart quotes
    clean_text = text_content.replace('₹', 'Rs.').replace('—', '-').replace('’', "'").replace('“', '"').replace('”', '"')
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output()

def extract_metadata(text):
    # Quick regex for dashboard metrics
    deadline = re.search(r"(\d{2}[-/]\d{2}[-/]\d{4})", text)
    emd = re.search(r"(?:EMD|Earnest Money).*?(?:Rs\.?|INR)?\s?([\d,.]+)", text, re.IGNORECASE)
    return {
        "deadline": deadline.group(1) if deadline else "Not Detected",
        "emd": emd.group(1) if emd else "TBD"
    }

# --- 3. PAGE SETUP & CSS ---
st.set_page_config(page_title="SafeDraft AI | Indian Bank", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp {
        background: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: white !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        border: 1px solid #e2e8f0 !important;
    }
    /* Custom Blue Buttons */
    div.stButton > button:first-child {
        background-color: #00529b !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100%;
        height: 3em;
    }
    /* Tab Selection */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. API & CLIENT INITIALIZATION ---
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.info("👈 Enter Gemini API Key in the sidebar to initialize the Banking Engine.")
    st.stop()

# Initialize the NEW 2026 Client
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash" 

# --- 5. SIDEBAR: KNOWLEDGE MEMORY ---
st.sidebar.title("🏦 Indian Bank x VIT")
st.sidebar.caption("FinTech Cybersecurity Hackathon 2025")

uploaded_files = st.sidebar.file_uploader("Knowledge Memory: Upload Past RFPs", type="pdf", accept_multiple_files=True)

all_text = ""
if uploaded_files:
    with st.sidebar.status("🔄 Ingesting Documents...") as status:
        for file in uploaded_files:
            reader = PdfReader(file)
            all_text += "".join([page.extract_text() for page in reader.pages])
        meta = extract_metadata(all_text)
        status.update(label="Knowledge Base Ready", state="complete")
    
    st.sidebar.divider()
    st.sidebar.metric("Target Deadline", meta['deadline'])
    st.sidebar.metric("EMD Detected", f"Rs. {meta['emd']}")
    
    # Compliance Score Logic
    score = 0
    if "EMD" in all_text or "Earnest" in all_text: score += 25
    if "Cyber" in all_text or "Security" in all_text: score += 25
    if "SLA" in all_text: score += 25
    if "Termination" in all_text: score += 25
    st.sidebar.metric("Compliance Health", f"{score}%")

# --- 6. MAIN WORKSPACE ---
st.title("Auto-RFP: Intelligent Lifecycle Management")
tab1, tab2, tab3 = st.tabs(["📜 Smart Drafting", "🔍 Grounded QA", "📑 Corrigendum"])

with tab1:
    st.subheader("Smart Drafting Engine")
    context = st.text_area("RFP Section Description:", placeholder="e.g. Technical specifications for AI-based fraud detection system...")
    if st.button("Generate Official Draft"):
        if not all_text: st.warning("Please upload reference RFPs in the sidebar first for better context."); context_prompt = ""
        else: context_prompt = f"Based on past tenders: {all_text[:12000]}"
        
        with st.status("🛠️ Drafting with Banking Logic...") as s:
            prompt = f"{SYSTEM_PROMPT}\n\n{context_prompt}\n\nDraft a formal RFP section for: {context}"
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            st.markdown(response.text)
            st.download_button("Download as PDF", data=create_pdf(response.text), file_name="RFP_Section_Draft.pdf")
            s.update(label="Draft Ready for Review!", state="complete")

with tab2:
    st.subheader("Grounded Query Assistant")
    query = st.text_input("Ask a specific question (e.g., 'What are the eligibility criteria for vendors?')")
    if query:
        if not all_text:
            st.error("No documents in memory. Upload PDFs to use the Query Assistant.")
        else:
            with st.status("Analyzing Sources...") as s:
                prompt = f"{SYSTEM_PROMPT}\n\nContext: {all_text[:25000]}\n\nQuestion: {query}\n\nProvide a precise answer and quote the section."
                response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                st.info(response.text)
                s.update(label="Answer Grounded in RFP", state="complete")

with tab3:
    st.subheader("Corrigendum Generator")
    raw_queries = st.text_area("Paste Vendor Clarification Requests (one per line):")
    if st.button("Generate Official Corrigendum"):
        with st.status("Structuring Corrigendum Table...") as s:
            prompt = f"{SYSTEM_PROMPT}\n\nCreate a formal Corrigendum table with columns: 'Vendor Query' and 'Bank's Clarification/Amendment'.\nQueries: {raw_queries}"
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            st.markdown(response.text)
            st.download_button("Download Corrigendum PDF", data=create_pdf(response.text), file_name="Official_Corrigendum.pdf")
            s.update(label="Corrigendum Published", state="complete")