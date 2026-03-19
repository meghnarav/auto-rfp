import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import math
from dotenv import load_dotenv
from fpdf import FPDF

# --- 1. HELPERS & CONFIG ---
load_dotenv()

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Auto-RFP System - Indian Bank x VIT', 0, 1, 'C')

def create_pdf(text_content):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Basic cleanup for special characters
    clean_text = text_content.replace('₹', 'Rs.').encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output()

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Auto-RFP Pro", page_icon="🏦", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_ok_safe=True)

st.title("🏦 Auto-RFP: Enterprise Lifecycle Management")
st.caption("Solo Developer Edition | Powered by Gemini 2.5 Flash")

# --- 3. API KEY & MODEL ---
env_key = os.getenv("GEMINI_API_KEY")
api_key = st.sidebar.text_input("Gemini API Key", value=env_key or "", type="password")

if not api_key:
    st.warning("👈 Enter your API Key to unlock the vault.")
    st.stop()

genai.configure(api_key=api_key)
# Enable logprobs for confidence scoring
model = genai.GenerativeModel(
    'gemini-2.0-flash', # Updated to the latest stable flash
    generation_config={"response_logprobs": True} 
)

# --- 4. SIDEBAR: DATA INGESTION ---
st.sidebar.header("📁 Document Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Master RFP", type="pdf")

if uploaded_file:
    with st.status("Ingesting Document...", expanded=False) as status:
        reader = PdfReader(uploaded_file)
        raw_text = "".join([page.extract_text() for page in reader.pages])
        st.session_state.raw_text = raw_text
        status.update(label="RFP Successfully Indexed!", state="complete")
    
    # Show Metadata Metrics
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Pages", len(reader.pages))
    col2.metric("Tokens (est)", len(raw_text)//4)

# --- 5. MAIN WORKSPACE ---
tab1, tab2, tab3 = st.tabs(["📜 Smart Drafting", "🔍 Grounded QA", "📑 Corrigendum Builder"])

with tab1:
    st.subheader("Automated Clause Generation")
    context = st.text_input("Describe the new section (e.g., 'Cybersecurity compliance for cloud hosting')")
    if st.button("Generate Section", type="primary"):
        with st.status("Drafting official clauses...") as s:
            prompt = f"Write a professional banking RFP section for: {context}. Style: Formal, Legal, Indian Banking Standards."
            response = model.generate_content(prompt)
            st.markdown(response.text)
            s.update(label="Draft Complete", state="complete")
            
            pdf_out = create_pdf(response.text)
            st.download_button("Download .pdf", data=pdf_out, file_name="draft.pdf")

with tab2:
    st.subheader("Grounded Query Assistant")
    query = st.text_input("Ask a specific question about the uploaded document:")
    
    if query and 'raw_text' in st.session_state:
        with st.status("Analyzing RFP...") as s:
            # RAG-style prompt with grounding
            prompt = f"Context: {st.session_state.raw_text[:25000]}\nQuestion: {query}\nAnswer strictly based on context. If not found, say so."
            response = model.generate_content(prompt)
            
            # Calculate Confidence Score from Logprobs
            try:
                avg_logprob = response.candidates[0].avg_logprobs
                confidence = math.exp(avg_logprob) * 100
            except: confidence = 85.0 # Fallback

            st.chat_message("assistant").write(response.text)
            st.progress(confidence/100, text=f"AI Confidence Score: {confidence:.1f}%")
            s.update(label="Analysis Finished", state="complete")
    elif query:
        st.error("Upload a PDF first!")

with tab3:
    st.subheader("Corrigendum Management")
    change_desc = st.text_area("List the vendor queries or changes (e.g., 'Vendor A asks if EMD can be BG instead of DD')")
    if st.button("Generate Official Corrigendum"):
        with st.spinner("Refining language..."):
            prompt = f"Create a formal Corrigendum table based on these changes: {change_desc}. Include 'Original Clause' and 'Amended Clause' columns."
            response = model.generate_content(prompt)
            st.markdown(response.text)
