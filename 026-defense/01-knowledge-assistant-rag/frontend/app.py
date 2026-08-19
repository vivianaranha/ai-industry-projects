"""Streamlit user interface for the project.

The UI intentionally exposes both text and numeric inputs because the generated
repository contains many AI task types. The backend decides which inputs matter
for this particular project.
"""
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Use Case", layout="wide")
st.title("AI Industry Use Case")

try:
    meta = requests.get(f"{API_URL}/metadata", timeout=5).json()
    st.subheader(meta["use_case"])
    st.caption(f"Industry: {meta['industry']} • Task: {meta['task_type']}")
except Exception:
    meta = {"task_type": "unknown", "industry": "unknown", "use_case": "unknown"}
    st.warning("Backend is not reachable yet. Start it with: python scripts/run_backend.py")

with st.form("inference_form"):
    text = st.text_area("Text / question / business context", height=180, placeholder="Enter a question, document, issue, goal, or business context...")
    st.markdown("**Optional numeric features**")
    c1, c2, c3 = st.columns(3)
    x1 = c1.number_input("x1", value=0.0)
    x2 = c2.number_input("x2", value=0.0)
    x3 = c3.number_input("x3", value=0.0)
    c4, c5 = st.columns(2)
    budget = c4.number_input("budget", value=100.0, min_value=0.0)
    horizon = int(c5.number_input("forecast horizon", value=7, min_value=1, max_value=90))
    submitted = st.form_submit_button("Run AI Use Case", type="primary")

if submitted:
    payload = {"text": text, "features": {"x1": x1, "x2": x2, "x3": x3, "budget": budget}, "options": {"horizon": horizon}}
    try:
        with st.spinner("Running the end-to-end workflow..."):
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=90)
            response.raise_for_status()
            result = response.json()
        st.success(f"Completed • Request ID {result['request_id']}")
        st.json(result["result"])
    except Exception as exc:
        st.error(f"Request failed: {exc}")

st.divider()
st.markdown("### Recent Requests")
if st.button("Refresh history"):
    try:
        history = requests.get(f"{API_URL}/history?limit=10", timeout=5).json()
        st.dataframe(history, use_container_width=True)
    except Exception as exc:
        st.error(f"Could not load history: {exc}")
