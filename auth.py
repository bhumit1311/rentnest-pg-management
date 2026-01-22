import streamlit as st
from datetime import datetime
from simple_database import SimplePGDatabase

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"

def login_page():
    """Display login page"""
    st.title("🏠 PG Management System")
    st.subheader("Login")
    
    tab1, tab2, tab3 = st.tabs(["Admin Login", "Renter Login", "Register as Renter"])
    
    with tab1:
        with st.form("admin_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login as Admin")
            
            if submit:
                db = SimplePGDatabase()
                admin = db.authenticate_admin(username, password)
                
                if admin:
                    st.session_state.authenticated = True
                    st.session_state.user_type = "admin"
                    st.session_state.user_id = admin[0]
                    st.session_state.user_name = admin[3]
                    st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("renter_login"):
            phone = st.text_input("Phone Number")
            submit = st.form_submit_button("Login as Renter")
            
            if submit:
                db = SimplePGDatabase()
                renter = db.authenticate_renter(phone)
                
                if renter:
                    st.session_state.authenticated = True
                    st.session_state.user_type = "renter"
                    st.session_state.user_id = renter[0]
                    st.session_state.user_name = renter[1]
                    st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid phone number or account not active")
    
    with tab3:
        st.subheader("Register as New Renter")
        with st.form("renter_registration"):
            name = st.text_input("Full Name*")
            phone = st.text_input("Phone Number*")
            email = st.text_input("Email (Optional)")
            join_date = st.date_input("Join Date", value=datetime.now().date())
            
            st.info("📝 After registration, please wait for admin approval to login")
            
            submit = st.form_submit_button("Register")
            
            if submit:
                if name and phone:
                    db = SimplePGDatabase()
                    success, message = db.add_renter(name, phone, email, join_date)
                    if success:
                        st.success(f"✅ {message}")
                        st.success(f"Your phone number: {phone}")
                        st.info("Please contact admin for approval and room allocation")
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all required fields (marked with *)")

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.login_time = None
    st.session_state.current_page = "dashboard"
    st.rerun()

def require_auth(user_type):
    """Require authentication"""
    if not st.session_state.authenticated or st.session_state.user_type != user_type:
        st.error("Unauthorized access")
        st.stop()