# superadmin_app.py
import streamlit as st
from db_utils import get_all_users, update_user_role_and_start, delete_user, get_pending_users, add_user, delete_pending_user
from datetime import datetime
from admin_utils import create_new_admin

def show_user_management():
    st.subheader("👥 Manage Registered Users")
    users = get_all_users()
    if not users:
        st.info("No registered users found.")
        return

    for username, role, start_date, *_ in users:
        with st.expander(f"🔸 {username}"):
            if role == "superadmin":
                st.markdown("✅ Superadmin (cannot modify)")
                continue

            new_role = st.selectbox("Role", ["admin", "agent"], index=["admin", "agent"].index(role), key=f"role_{username}")
            if isinstance(start_date, str):
                start_date_val = datetime.strptime(start_date, "%Y-%m-%d")
            else:
                start_date_val = start_date or datetime.today()

            new_start_date = st.date_input(
                "Start Date",
                value=start_date_val,
                key=f"date_{username}"
            )


            cols = st.columns(2)
            with cols[0]:
                if st.button("💾 Save Changes", key=f"save_{username}"):
                    update_user_role_and_start(username, new_role, new_start_date.strftime("%Y-%m-%d"))
                    st.success("✅ User updated.")
                    st.rerun()
            with cols[1]:
                if st.button("🗑️ Delete User", key=f"delete_{username}"):
                    delete_user(username)
                    st.warning(f"❌ User `{username}` deleted.")
                    st.rerun()


def show_pending_approvals():
    st.subheader("📝 Pending Admin Registrations")

    try:
        pending = get_pending_users()
        st.write(f"🔍 Total pending users: {len(pending)}")
    except Exception as e:
        st.error(f"❌ Could not load pending users: {e}")
        return

    pending_admins = [p for p in pending if p[3] == "admin"]
    st.write(f"🔍 Pending admins found: {len(pending_admins)}")

    if not pending_admins:
        st.success("✅ No pending admin registrations.")
        return

    for rowid, username, password, role, admin_username, db_name, do_code, agency_code in pending_admins:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(f"🔸 **{username}** | Role: `{role}` | DO Code: `{do_code}`")
        with col2:
            if st.button("✅ Approve", key=f"approve_{rowid}"):
                start_date = datetime.today().strftime("%Y-%m-%d")

                try:
                    st.info(f"✅ Adding user {username} to users table...")
                    add_user(username, password, role, start_date, None, db_name, do_code)
                    st.success("✅ Added to users table.")
                except Exception as e:
                    st.error(f"❌ Failed to add user: {e}")
                    return

                try:
                    st.info("🛠 Creating admin DB...")
                    create_new_admin(username=username, password=password, start_date=start_date)
                    st.success("✅ Admin DB created.")
                except Exception as e:
                    st.error(f"❌ Failed to create DB: {e}")
                    return

                try:
                    st.info(f"🗑️ Deleting pending user ID: {rowid}")
                    delete_pending_user(rowid)
                    st.success(f"✅ Deleted pending record for `{username}`.")
                except Exception as e:
                    st.error(f"❌ Failed to delete from pending_users: {e}")
                    return
                st.rerun()

        with col3:
            if st.button("❌ Reject", key=f"reject_{rowid}"):
                delete_pending_user(rowid)
                st.warning(f"❌ Registration for `{username}` rejected.")
                st.rerun()

def superadmin_dashboard():
    st.title("🛡️ Superadmin Panel")
    show_pending_approvals()
    st.markdown("---")
    show_user_management()


