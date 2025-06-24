# approval_ui.py

import streamlit as st
from db_utils import get_pending_users, delete_pending_user, add_user_to_db  # ya aapka jo actual import ho

def show_approval_ui():
    st.header("🚦 Pending User Approvals")

    pending_users = get_pending_users()

    if not pending_users:
        st.success("✅ No users pending approval.")
        return

    for user in pending_users:
        row_id, username, password, role, admin_username, db_name, do_code, agency_code, name = user

        with st.expander(f"👤 {name} ({username}) - {role}"):
            st.text(f"Username: {username}")
            st.text(f"Role: {role}")
            st.text(f"Admin: {admin_username}")
            st.text(f"Agency Code: {agency_code or 'N/A'}")
            st.text(f"DO Code: {do_code or 'N/A'}")
            st.text(f"DB Name: {db_name}")
            st.text(f"Name: {name}")

            if st.button(f"✅ Approve {username}", key=f"approve_{row_id}"):
                try:
                    add_user_to_db(
                        username=username.upper(),
                        password=password,
                        role=role,
                        admin_username=admin_username,
                        db_name=db_name,
                        do_code=do_code,
                        agency_code=agency_code,
                        name=name
                    )
                    delete_pending_user(row_id)
                    st.success(f"✅ {username} approved successfully!")
                    st.experimental_rerun()

                except Exception as e:
                    st.error(f"❌ Failed to approve {username}: {e}")
