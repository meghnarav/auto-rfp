import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv
from fpdf import FPDF
import re

# --- 1. CONFIG & SYSTEM PROMPT ---
load_dotenv()
SYSTEM_PROMPT = "You are an expert Banking Procurement Officer at Indian Bank. Use formal, legally-compliant language. Always refer to banking standards and DFS/IBA guidelines."

# --- 2. HELPERS ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Fixing the Latin-1/Rupee crash:
    clean_text = text_content.replace('₹', 'Rs.').replace('"', '"').replace('"', '"')
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S')

def extract_metadata(text):
    # Quick regex vibe-check for metadata
    deadline = re.search(r"(\d{2}[-/]\d{2}[-/]\d{4})", text)
    emd = re.search(r"(EMD|Earnest Money).*?(\d+[,.]\d+)", text)
    return {
        "deadline": deadline.group(1) if deadline else "Not Detected",
        "emd": emd.group(2) if emd else "TBD"
    }

# --- 3. PAGE SETUP ---
st.set_page_config(page_title="SafeDraft AI | Indian Bank", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Sidebar "Glass" Effect */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* Metric Cards - React Style */
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid #edf2f7;
    }

    /* Tab Styling - The "Shadcn" Look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        background-color: transparent;
        border: none;
        color: #64748b;
        transition: all 0.2s;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #00529b !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Big Blue "Action" Button */
    .stButton>button {
        background: linear-gradient(90deg, #00529b 0%, #0073cf 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: transform 0.1s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 82, 155, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. API & MODEL ---
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.info("👈 Enter API Key to begin.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # Using 1.5 for better context handling

# --- 5. SIDEBAR: BRANDING & METRICS ---
st.sidebar.title("🏦 Indian Bank x VIT")
st.sidebar.caption("FinTech Cybersecurity Hackathon 2025")

uploaded_files = st.sidebar.file_uploader("Knowledge Memory: Upload Past RFPs", type="pdf", accept_multiple_files=True)

all_text = ""
if uploaded_files:
    with st.sidebar.status("🔄 Processing Documents...") as status:
        for file in uploaded_files:
            reader = PdfReader(file)
            all_text += "".join([page.extract_text() for page in reader.pages])
        meta = extract_metadata(all_text)
        status.update(label="System Ready", state="complete")
    
    st.sidebar.divider()
    st.sidebar.metric("Detected Deadline", meta['deadline'])
    st.sidebar.metric("EMD Amount", f"Rs. {meta['emd']}")
    st.sidebar.metric("Total Documents", len(uploaded_files))

# --- 6. MAIN WORKSPACE ---
st.title("Auto-RFP: Lifecycle Management")
tab1, tab2, tab3 = st.tabs(["📜 Drafting", "🔍 Grounded QA", "📑 Corrigendum"])

with tab1:
    st.subheader("Smart Drafting Engine")
    context = st.text_area("RFP Section Description:", placeholder="e.g. Technical requirements for UPI Switch upgrade...")
    if st.button("Generate Official Draft", type="primary"):
        with st.status("🛠️ Working...") as s:
            s.write("Applying Banking Rules...")
            s.write("Consulting Knowledge Memory...")
            prompt = f"{SYSTEM_PROMPT}\n\nBased on past tenders: {all_text[:10000]}\n\nDraft a formal RFP section for: {context}"
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.download_button("Download Draft", data=create_pdf(response.text), file_name="RFP_Draft.pdf")
            s.update(label="Draft Complete!", state="complete")

with tab2:
    st.subheader("Grounded Query Assistant")
    query = st.text_input("Ask about the uploaded documents:")
    if query and all_text:
        with st.status("Searching Sources...") as s:
            prompt = f"{SYSTEM_PROMPT}\n\nStrictly answer using this context: {all_text[:30000]}\n\nQuestion: {query}\n\nFormat your answer as:\nANSWER: [Text]\nSOURCE SNIPPET: [3 lines of original text from document]"
            response = model.generate_content(prompt)
            st.info(response.text)
            s.update(label="Verified Answer Found", state="complete")

with tab3:
    st.subheader("Corrigendum Engine")
    raw_queries = st.text_area("Paste Vendor Queries:")
    if st.button("Generate Corrigendum Table"):
        with st.status("Structuring Data...") as s:
            prompt = f"{SYSTEM_PROMPT}\n\nConvert these queries into a formal bank corrigendum table with 'Reference Clause', 'Query', and 'Clarification' columns. Queries: {raw_queries}"
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.download_button("Download Official Corrigendum", data=create_pdf(response.text), file_name="Corrigendum.pdf")
            s.update(label="Table Published", state="complete")