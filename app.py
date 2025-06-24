# app.py (modularized entry point)
import streamlit as st
import mysql.connector  # Fails if not installed
#from login_router import route_dashboard

st.set_page_config(
    layout="centered",
    page_title="LIC Udaan Portal",
    page_icon="📄"
)

# Initialize session state defaults
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["start_date"] = ""
    st.session_state["selected_year"] = "All Years"
    st.session_state["fin_year"] = "All Financial Years"
    st.session_state["show_pending"] = False
    st.session_state["show_registration_form"] = False

try:
    from login_router import route_dashboard
    route_dashboard()
except Exception as e:
    st.error(f"❌ Failed to load login router: {e}")
    st.stop()
# Route to login or role-specific dashboard
#route_dashboard()
