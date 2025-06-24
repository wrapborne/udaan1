# utils.py
import pandas as pd
import streamlit as st
from sqlalchemy import text
from sqlalchemy import create_engine
from db_config import DB_CONFIG
from db_utils import get_mysql_connection

# utils.py or logging_utils.py
from datetime import datetime

from db_utils import get_mysql_connection
import pandas as pd

from db_utils import get_admin_by_do_code, user_exists, add_pending_user

def get_financial_year_options(start_year=1956):
    today = datetime.today()
    current_year = today.year + (1 if today.month >= 4 else 0)
    options = ["All Financial Years"]

    for year in range(start_year, current_year + 1):
        options.append(f"{year-1}-{year}")

    return options

def get_agency_year_ranges(start_date_str):
    """Returns agency year ranges from start_date to current date."""
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    except Exception as e:
        return ["All Years"]

    today = datetime.today()
    options = ["All Years"]

    while start_date < today:
        end_date = start_date.replace(year=start_date.year + 1) - pd.Timedelta(days=1)
        options.append(f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        start_date = end_date + pd.Timedelta(days=1)

    return options

def handle_registration(username, password, do_code, role, name, agency_code=None):
    # 🚫 Validate required fields
    if username is None or not str(username).strip():
        st.error("❌ Username is required.")
        return

    if password is None or not str(password).strip():
        st.error("❌ Password is required.")
        return

    if do_code is None or not str(do_code).strip():
        st.error("❌ DO Code is required.")
        return

    if role not in ("admin", "agent"):
        st.error("❌ Invalid role selected.")
        return

    if role == "agent" and (agency_code is None or not str(agency_code).strip()):
        st.error("❌ Agency Code is required for agent.")
        return

    # ✅ Clean input
    username_clean = str(username).strip().upper()
    do_code_clean = str(do_code).strip().upper()

    # 🔍 Check if username exists
    if user_exists(username_clean):
        st.error("❌ Username already exists.")
        return

    if len(password.strip()) < 4:
        st.warning("⚠️ Password must be at least 4 characters.")
        return

    # === Agent Logic ===
    if role == "agent":
        admin_data = get_admin_by_do_code(do_code_clean)
        if not admin_data:
            st.error("❌ Invalid DO Code. Please check with your admin.")
            return

        try:
            engine = get_mysql_connection(admin_data["db_name"])
            with engine.connect() as conn:
                result = conn.execute(text("SELECT DISTINCT `Agency Code` FROM lic_data"))
                agency_codes = [row[0].strip().upper() for row in result.fetchall()]


            if agency_code.strip().upper() not in agency_codes:
                st.error("❌ Invalid Agency Code. Contact your admin.")
                return
        except Exception as e:
            st.error(f"❌ Failed to validate agency code: {e}")
            return

        admin_username = admin_data["username"]
        db_name = admin_data["db_name"]

    # === Admin Logic ===
    elif role == "admin":
        admin_username = None
        db_name = f"lic_{username_clean}"

    # ✅ Insert into pending_users
    add_pending_user(
        username=username_clean,
        password=password,
        role=role,
    #    start_date=datetime.today().strftime("%Y-%m-%d"),
        admin_username=admin_username,
        db_name=db_name,
        do_code=do_code,
        agency_code=agency_code.strip().upper() if agency_code else None
    )

    st.success("✅ Registration submitted. Admin will approve your account.")




def log_login(username):
    with open("login_log.txt", "a") as f:
        f.write(f"{username} logged in at {datetime.now():%Y-%m-%d %H:%M:%S}\n")


def get_mysql_connection(db_name=None):
    """Returns a SQLAlchemy engine for the given database."""
    if db_name is None:
        db_name = DB_CONFIG["database"]

    return create_engine(
        f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{db_name}"
    )

def load_lic_data_from_db():
    engine = get_mysql_connection(st.session_state["db_name"])
    try:
        df = pd.read_sql("SELECT * FROM lic_data", con=engine)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        df = pd.DataFrame()
    return df

def get_policy_count_by_plan(df):
    if "Plan" not in df.columns or df["Plan"].dropna().empty:
        return pd.DataFrame()
    plan_counts = df["Plan"].value_counts(dropna=True)
    if plan_counts.empty:
        return pd.DataFrame()
    plan_counts_df = pd.DataFrame(plan_counts).T
    plan_counts_df.index = ["Policy Count"]
    plan_counts_df.columns = plan_counts_df.columns.astype(str)
    return plan_counts_df

def filter_df_by_selected_year(df, selected_year):
    if selected_year == "All Years":
        return df
    try:
        start_str, end_str = selected_year.split(" - ")
        start_date = datetime.strptime(start_str.strip(), "%d/%m/%Y")
        end_date = datetime.strptime(end_str.strip(), "%d/%m/%Y")
        df["DOC"] = pd.to_datetime(df["DOC"], errors="coerce")
        return df[(df["DOC"] >= start_date) & (df["DOC"] <= end_date)]
    except:
        return df

def filter_df_by_financial_year(df, selected_fin_year):
    if selected_fin_year == "All Financial Years":
        return df
    try:
        start_year, end_year = map(int, selected_fin_year.split("-"))
        start_date = datetime(start_year, 4, 1)
        end_date = datetime(end_year, 3, 31)
        df["DOC"] = pd.to_datetime(df["DOC"], errors="coerce")
        return df[(df["DOC"] >= start_date) & (df["DOC"] <= end_date)]
    except:
        return df
