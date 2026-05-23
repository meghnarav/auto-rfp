# Auto-RFP

A simple AI-assisted tool to help draft and review banking RFP (Request for Proposal) documents using Gemini and Streamlit.

---

## What this is

Auto-RFP is a lightweight internal tool that helps speed up common RFP-related work like drafting sections, answering questions from past documents, and generating corrigendum responses.

It is not a full enterprise system. It’s a working prototype built to explore how LLMs can fit into procurement workflows.

---

## Features

### 1. RFP Drafting
- Takes a section description as input
- Uses uploaded past RFP PDFs as reference context
- Generates a formal draft in a banking-style tone

### 2. Document Q&A
- Ask questions over uploaded RFP documents
- Extracts answers using full-text context from PDFs
- Useful for checking clauses, requirements, and eligibility rules

### 3. Corrigendum Generator
- Converts vendor clarification questions into a structured response table
- Outputs formatted text suitable for official documentation

---

## Tech Stack

- Python
- Streamlit
- Google Gemini API (gemini-2.0-flash)
- PyPDF (PDF text extraction)
- FPDF (PDF export)
- dotenv

---

## How it works

1. Upload past RFP documents (PDFs)
2. System extracts text from all documents
3. User enters a prompt or question
4. Prompt is combined with document context
5. Gemini generates a response
6. Output is shown in UI and can be downloaded as PDF

---

## Example

**Input:**
> Technical specifications for an AI-based fraud detection system

**Output:**
- Formal RFP section written in structured banking language
- Aligned with compliance tone used in procurement documents

---

## Limitations

- No backend or database
- No semantic search (pure text context injection)
- Limited by Gemini context window
- Works best for small-to-medium document sets
- Requires API key to run

---

## How to run

```bash
git clone https://github.com/your-username/auto-rfp.git
cd auto-rfp
pip install -r requirements.txt
```

Create a .env file:
```bash
GOOGLE_API_KEY=your_api_key_here
```

Run the app:
```bash
streamlit run app.py
```

---

## Notes
This project was built to explore how LLMs can reduce manual effort in drafting and reviewing banking procurement documents. It focuses more on usability and workflow speed than system complexity.

---

## Future Improvements
- Add semantic search over documents (vector DB)
- Better citation of source sections in answers
- Role-based templates (legal, technical, procurement)
- Move from Streamlit to proper web app architecture

---

Copyright (c) 2026 Meghna Ravikumar. All rights reserved. No part of this software may be reproduced or distributed without permission.
