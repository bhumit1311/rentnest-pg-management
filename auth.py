import streamlit as st
from datetime import datetime

from simple_database import SimplePGDatabase
from session_manager import SessionManager


# --------------------------------------------------
# 1️⃣ INITIALIZE SESSION STATE ONCE (CRITICAL)
# --------------------------------------------------
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())


# 🔴 MUST be called before ANY auth check
init_session_state()
SessionManager.init()


# --------------------------------------------------
# 2️⃣ AUTH GUARD (DO NOT CHECK logged_in DIRECTLY)
# --------------------------------------------------
if not st.session_state.authenticated:
    login_page_placeholder = True
else:
    login_page_placeholder = False


# --------------------------------------------------
# 3️⃣ LOGIN PAGE
# --------------------------------------------------
def login_page():
    st.title("🏠 PG Management System")
    st.subheader("Login")

    tab1, tab2, tab3 = st.tabs(
        ["Admin Login", "Renter Login", "Register as Renter"]
    )

    # -------- Admin Login --------
    with tab1:
        with st.form("admin_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login as Admin")

            if submit:
                if username and password:
                    db = SimplePGDatabase()
                    admin = db.authenticate_admin(username, password)
                    
                    if admin:
                        # admin tuple: (admin_id, username, password, name)
                        SessionManager.save_login(
                            user_id=admin[0],
                            user_type="admin",
                            user_name=admin[3],
                            username=admin[1],
                        )
                        st.session_state.authenticated = True
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")

    # -------- Renter Login --------
    with tab2:
        with st.form("renter_login"):
            phone = st.text_input("Phone Number")
            submit = st.form_submit_button("Login as Renter")

            if submit:
                if phone:
                    db = SimplePGDatabase()
                    renter = db.authenticate_renter(phone)
                    
                    if renter:
                        # renter tuple: (renter_id, name, phone, email, join_date, is_active)
                        SessionManager.save_login(
                            user_id=renter[0],
                            user_type="renter",
                            user_name=renter[1],
                        )
                        st.session_state.authenticated = True
                        st.success(f"✅ Welcome, {renter[1]}!")
                        st.rerun()
                    else:
                        st.error("❌ Phone number not found or account inactive")
                else:
                    st.warning("⚠️ Please enter your phone number")

    # -------- Registration --------
    with tab3:
        st.subheader("Register as New Renter")

        with st.form("renter_registration"):
            name = st.text_input("Full Name*")
            phone = st.text_input("Phone Number*")
            email = st.text_input("Email (Optional)")
            join_date = st.date_input(
                "Join Date", value=datetime.now().date()
            )

            st.info(
                "📝 After registration, please wait for admin approval to login"
            )

            submit = st.form_submit_button("Register")

            if submit:
                if name and phone:
                    db = SimplePGDatabase()
                    success, message = db.add_renter(
                        name, phone, email if email else None, join_date.strftime("%Y-%m-%d")
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.info("You can now login using your phone number")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please fill required fields (Name and Phone Number)")


# --------------------------------------------------
# 4️⃣ LOGOUT (FULL CLEAR — SAFE)
# --------------------------------------------------
def logout():
    SessionManager.clear_session()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# --------------------------------------------------
# 5️⃣ AUTH REQUIREMENT (USE EVERYWHERE)
# --------------------------------------------------
def require_auth(required_type=None):
    """Check if user is authenticated and has required user type"""
    if not st.session_state.authenticated:
        st.error("⚠️ Please login to access this page")
        st.stop()

    if required_type and st.session_state.user_type != required_type:
        st.error(f"⚠️ Access denied. This page requires {required_type} access.")
        st.stop()
