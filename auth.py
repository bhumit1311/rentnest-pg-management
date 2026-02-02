import streamlit as st
from datetime import datetime

from db.database import Database
from services.auth_service import AuthService
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
                try:
                    db = Database()
                    auth_service = AuthService(db)

                    success, user_data, message = auth_service.authenticate_admin(username, password)

                    if success and user_data:
                        SessionManager.save_login(
                            user_id=user_data['user_id'],
                            user_type="admin",
                            user_name=user_data['name'],
                            username=username,
                        )
                        st.session_state.authenticated = True
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

    # -------- Renter Login --------
    with tab2:
        with st.form("renter_login"):
            phone = st.text_input("Phone Number")
            submit = st.form_submit_button("Login as Renter")

            if submit:
                try:
                    db = Database()
                    auth_service = AuthService(db)

                    success, user_data, message = auth_service.authenticate_renter(phone)

                    if success and user_data:
                        SessionManager.save_login(
                            user_id=user_data['user_id'],
                            user_type="renter",
                            user_name=user_data['name'],
                        )
                        st.session_state.authenticated = True
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

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
                    try:
                        db = Database()
                        auth_service = AuthService(db)

                        success, message = auth_service.register_renter(
                            name, phone, email, join_date.strftime("%Y-%m-%d")
                        )
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(message)
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")
                else:
                    st.error("Please fill required fields (*)")


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
    if not st.session_state.authenticated:
        st.error("Please login")
        st.stop()

    if required_type:
        try:
            db = Database()
            auth_service = AuthService(db)

            if required_type == "admin":
                auth_service.require_admin(st.session_state.user_type, st.session_state.user_id)
            elif required_type == "renter":
                auth_service.require_renter(st.session_state.user_type, st.session_state.user_id)
        except Exception as e:
            st.error(f"Authorization failed: {str(e)}")
            st.stop()
