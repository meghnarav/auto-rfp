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

# --- 2. CUSTOM CSS ---

st.set_page_config(page_title="SafeDraft AI | Indian Bank", page_icon="🏦", layout="wide")

st.markdown("""
<style>
/* 1. Global Font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
.stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #fcfcfd !important;
}

/* 2. Hide Streamlit Branding */
.css-18e3th9 {visibility: hidden;}  /* top-right hamburger menu */
.css-1lsmgbg.egzxvld0 {visibility: hidden;} /* footer */

/* 3. Sidebar (Glassmorphism + subtle shadow) */
[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border-right: 1px solid #f1f5f9 !important;
    box-shadow: 4px 0 10px rgba(0,0,0,0.02);
}

/* 4. Metric Cards */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 20px !important;
    transition: all 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    border-color: #00529b !important;
}

/* 5. Primary Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #00529b 0%, #003d73 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.6rem 2rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}
button[kind="primary"]:hover {
    opacity: 0.9;
    transform: scale(1.02);
}

/* 6. Tabs Styling */
.css-1r6slb0 button {
    border-radius: 10px !important;
    background-color: transparent !important;
    border: none !important;
    color: #64748b !important;
    padding: 6px 12px;
    margin-right: 8px;
    transition: all 0.2s ease;
}
.css-1r6slb0 button[aria-selected="true"] {
    background-color: #ffffff !important;
    color: #00529b !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 7. Input fields (optional) */
.stTextInput>div>div>input {
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 0.5rem 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- 3.5. Demo Content ---
st.title("SafeDraft AI | Indian Bank")
st.subheader("Dashboard")
st.button("Primary Action")

tab1, tab2 = st.tabs(["Overview", "Transactions"])
with tab1:
    st.metric("Revenue", "$120K", "+12%")
with tab2:
    st.metric("Expenses", "$80K", "-5%")


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