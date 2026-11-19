# app.py
"""Streamlit UI for docdiff-auditor.

Allows users to upload two PDF documents or load built‑in sample contracts,
then extracts text chunks, embeds them with a sentence‑transformer model, and
classifies semantic changes.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from io import BytesIO

# Local imports
from core.extractor import extract_chunks
from core.comparator import (
    load_model,
    embed_chunks,
    compute_similarity_matrix,
    classify_changes,
)
from core.sample_docs import get_sample_pdfs

st.set_page_config(page_title="docdiff-auditor", layout="wide")

st.title("📄 DocDiff Auditor")
st.caption("Compare two PDF documents and detect semantic changes.")

# Sidebar sliders for thresholds
st.sidebar.header("Classification thresholds")
unchanged_thr = st.sidebar.slider("Unchanged similarity ≥", 0.80, 1.00, 0.92, 0.01)
modified_thr = st.sidebar.slider("Modified similarity ≥", 0.30, 0.99, 0.60, 0.01)
if modified_thr > unchanged_thr:
    st.sidebar.error("Modified threshold must be lower than Unchanged threshold.")
    st.stop()

# --- File inputs -----------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    uploaded_a = st.file_uploader("Document A (Baseline PDF)", type=["pdf"], key="doc_a")
with col2:
    uploaded_b = st.file_uploader("Document B (Revised PDF)", type=["pdf"], key="doc_b")

if st.button("Load Sample Contract Diff"):
    sample_a, sample_b = get_sample_pdfs()
    uploaded_a = BytesIO(sample_a)
    uploaded_a.name = "sample_a.pdf"
    uploaded_b = BytesIO(sample_b)
    uploaded_b.name = "sample_b.pdf"
    st.success("Sample contracts loaded.")

if not uploaded_a or not uploaded_b:
    st.info("Please provide both documents (or load the sample) to continue.")
    st.stop()

# Read PDF bytes
pdf_bytes_a = uploaded_a.read()
pdf_bytes_b = uploaded_b.read()

# --- Extraction -----------------------------------------------------------
chunks_a = extract_chunks(pdf_bytes_a)
chunks_b = extract_chunks(pdf_bytes_b)

st.subheader("Extracted chunks")
st.write(f"Document A: {len(chunks_a)} chunks, Document B: {len(chunks_b)} chunks")

# --- Embedding ------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_model():
    return load_model()

model = get_model()
emb_a = embed_chunks(chunks_a, model)
emb_b = embed_chunks(chunks_b, model)

# --- Similarity & Classification ------------------------------------------
sim_matrix = compute_similarity_matrix(emb_a, emb_b)
results = classify_changes(
    chunks_a,
    chunks_b,
    sim_matrix,
    unchanged_thr=unchanged_thr,
    modified_thr=modified_thr,
)

# Summarize counts
summary = pd.DataFrame(results)["status"].value_counts().to_dict()
st.metric("Unchanged", summary.get("Unchanged", 0))
st.metric("Modified", summary.get("Modified", 0))
st.metric("Added", summary.get("Added", 0))
st.metric("Removed", summary.get("Removed", 0))

# --- Detailed view --------------------------------------------------------
st.subheader("Changes")
for i, entry in enumerate(results):
    status = entry["status"]
    color = {
        "Unchanged": "green",
        "Modified": "orange",
        "Added": "blue",
        "Removed": "red",
    }.get(status, "gray")
    with st.expander(f"{i+1}. [{status}] similarity: {entry.get('similarity', 'N/A'):.2f}"):
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"**Baseline**")
            if entry["a_text"]:
                st.write(entry["a_text"])
            else:
                st.write("*None*")
        with cols[1]:
            st.markdown(f"**Revised**")
            if entry["b_text"]:
                st.write(entry["b_text"])
            else:
                st.write("*None*")
        st.markdown(f"<span style='color:{color};font-weight:bold'>{status}</span>", unsafe_allow_html=True)

# --- Export ---------------------------------------------------------------
if st.button("Download Audit Report (CSV)"):
    df = pd.DataFrame(results)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV", data=csv, file_name="docdiff_audit.csv", mime="text/csv")

if st.button("Download Audit Report (JSON)"):
    json_str = json.dumps(results, indent=2)
    st.download_button("📥 JSON", data=json_str, file_name="docdiff_audit.json", mime="application/json")
