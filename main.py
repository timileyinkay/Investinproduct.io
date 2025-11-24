import streamlit as st

st.set_page_config(page_title="Power Bank Dashboard", page_icon="🔋")
st.title("🔋 Power Bank Investment Dashboard")
st.write("Dashboard is loading...")

# Simple test to see if app works
st.success("Application is running successfully!")
st.metric("Test Metric", value=100, delta=10)