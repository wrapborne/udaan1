# layout.py
import streamlit as st
from datetime import datetime
from utils import get_agency_year_ranges, get_financial_year_options

def render_sidebar():
    role = st.session_state.get("role", "")
    full_name = st.session_state.get("name", st.session_state.get("username", "User")).title()

    st.sidebar.title("🌟 Welcome")

    # 👋 Greeting
    st.sidebar.markdown(f"**Hello, {full_name}!**")
#    st.sidebar.markdown(f"🧾 Role: `{role.capitalize()}`")

    # Filters based on role
    if role == "admin":
        render_year_filters(st.session_state.get("start_date"), prefix="admin")
    elif role == "agent":
        render_year_filters(st.session_state.get("start_date"), prefix="agent")

    # Divider and logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()


def render_year_filters(start_date, prefix=""):
    if isinstance(start_date, datetime):
        start_str = start_date.strftime("%Y-%m-%d")
    else:
        start_str = str(start_date)

    year_options = get_agency_year_ranges(start_str)
    fin_year_options = get_financial_year_options()

    prefix = "agent" if st.session_state.role == "agent" else "admin"
    label = "📆 Agency Year" if st.session_state.role == "agent" else "📆 Appraisal Year"

    selected_year = st.sidebar.selectbox(
        label,
        year_options,
        key=f"{prefix}_selected_year"
    )

    st.session_state.selected_year = selected_year

    selected_fin = st.sidebar.selectbox(
        "💰 Financial Year", fin_year_options,
        key=f"{prefix}_fin_year"
    )

    st.session_state["selected_year"] = selected_year
    st.session_state["fin_year"] = selected_fin
