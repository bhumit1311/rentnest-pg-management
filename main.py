import streamlit as st
from auth import init_session_state, login_page, logout, require_auth
from admin_panel import (
    admin_dashboard, room_management, renter_management, registration_management,
    payment_management, complaint_management, reports
)
from renter_panel import (
    renter_dashboard, my_payments, my_complaints,
    my_profile, notifications
)
from init_data import initialize_database

# Page configuration with full width layout
st.set_page_config(
    page_title="RentNest - Smart Living Management",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# Enhanced CSS for top navigation and full-width design
st.markdown("""
<style>
    /* Hide default sidebar and streamlit elements */
    .css-1d391kg {display: none;}
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: none;
        background: #f5f7fa;
    }
    
    /* Top Navigation Bar - Modern Clean Design */
    .top-nav {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        margin: -1rem -1.5rem 1.5rem -1.5rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
    }
    
    .nav-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
        letter-spacing: 0.5px;
    }
    
    .nav-subtitle {
        color: rgba(255, 255, 255, 0.95);
        text-align: center;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
        font-weight: 300;
    }
    
    .user-info {
        position: absolute;
        top: 1.5rem;
        right: 2rem;
        color: white;
        text-align: right;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Content area styling - Clean Card Design */
    .content-area {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        border: 1px solid #e8ecf1;
    }
    
    /* Streamlit Elements Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fb;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        background: transparent;
        border: none;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab"] button {
        color: #2d3748 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    .stTabs [aria-selected="true"] button {
        color: #667eea !important;
    }
    
    /* Form Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1.5px solid #e8ecf1;
        padding: 0.6rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        color: #2d3748 !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Form Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label,
    .stDateInput > label,
    .stFileUploader > label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Form Label Text */
    .stTextInput label p,
    .stTextArea label p,
    .stSelectbox label p,
    .stNumberInput label p,
    .stDateInput label p,
    .stFileUploader label p {
        color: #2d3748 !important;
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a5568 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* General Text Visibility */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: #2d3748 !important;
    }
    
    /* Streamlit Markdown */
    .stMarkdown {
        color: #2d3748 !important;
    }
    
    .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: #2d3748 !important;
    }
    
    /* Info/Warning/Success/Error Text */
    .stAlert p {
        color: inherit !important;
    }
    
    /* Form Submit Button Text */
    .stFormSubmitButton button {
        color: white !important;
    }
    
    /* Checkbox and Radio Text */
    .stCheckbox label,
    .stRadio label {
        color: #2d3748 !important;
    }
    
    .stCheckbox label span,
    .stRadio label span {
        color: #2d3748 !important;
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e8ecf1;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: #f8f9fb;
        border-radius: 10px;
        padding: 1rem;
        font-weight: 600;
        border: 1px solid #e8ecf1;
        color: #2d3748 !important;
    }
    
    .streamlit-expanderHeader p,
    .streamlit-expanderHeader span,
    .streamlit-expanderHeader div {
        color: #2d3748 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f1f3f6;
    }
    
    .streamlit-expanderContent {
        color: #2d3748 !important;
    }
    
    .streamlit-expanderContent p,
    .streamlit-expanderContent span,
    .streamlit-expanderContent div {
        color: #2d3748 !important;
    }
    
    /* Alert Messages - Clean Design */
    .stAlert {
        border-radius: 10px;
        border: none;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    /* Footer - Minimal */
    .footer {
        background: white;
        padding: 1.5rem;
        margin: 1.5rem -1.5rem -1rem -1.5rem;
        border-radius: 20px 20px 0 0;
        text-align: center;
        color: #718096;
        border-top: 1px solid #e8ecf1;
        font-size: 0.85rem;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e8ecf1;
    }
    
    /* Hide horizontal rule after navigation buttons */
    .main .block-container > div:first-child hr:first-of-type {
        display: none;
    }
    
    /* Better spacing for button rows */
    .row-widget.stHorizontal {
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-info {
            position: static;
            text-align: center;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .top-nav {
            padding: 1rem;
        }
        
        .content-area {
            padding: 1.5rem;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f3f6;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a0aec0;
    }
    
    /* Additional Text Visibility Fixes */
    .element-container p,
    .element-container span,
    .element-container div {
        color: #2d3748 !important;
    }
    
    /* Ensure all text in forms is visible */
    form p, form span, form div, form label {
        color: #2d3748 !important;
    }
    
    /* Select box options */
    .stSelectbox div[data-baseweb="select"] {
        color: #2d3748 !important;
    }
    
    /* Date input text */
    .stDateInput input {
        color: #2d3748 !important;
    }
    
    /* Text area placeholder */
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: #718096 !important;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

def show_top_navigation():
    """Show top navigation bar with user info"""
    if st.session_state.authenticated:
        user_type_display = st.session_state.user_type.title()
        
        if st.session_state.user_type == "admin":
            nav_title = "🏠 RentNest - Admin Dashboard"
            nav_subtitle = "Comprehensive Smart Living Management Platform"
        else:
            nav_title = "🏠 RentNest - Resident Portal"
            nav_subtitle = "Your Smart Living Experience Hub"
        
        st.markdown(f"""
        <div class="top-nav">
            <div class="user-info">
                <strong>{st.session_state.user_name}</strong><br>
                <small>{user_type_display} • {st.session_state.get('login_time', 'N/A')}</small>
            </div>
            <h1 class="nav-title">{nav_title}</h1>
            <p class="nav-subtitle">{nav_subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

def show_navigation_menu():
    """Show horizontal navigation menu"""
    if not st.session_state.authenticated:
        return
    
    # Initialize current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Define navigation based on user type
    if st.session_state.user_type == "admin":
        nav_items = {
            "📊 Dashboard": "dashboard",
            "🏠 Rooms": "rooms",
            "👥 Residents": "renters",
            "📋 Registrations": "registrations",
            "💰 Payments": "payments",
            "📝 Complaints": "complaints",
            "📊 Reports": "reports"
        }
    else:
        nav_items = {
            "🏠 My Dashboard": "dashboard",
            "💰 My Payments": "payments",
            "📝 My Complaints": "complaints",
            "👤 My Profile": "profile",
            "🔔 Notifications": "notifications"
        }
    
    # Handle navigation with columns for buttons
    cols = st.columns(len(nav_items) + 1)
    
    for i, (nav_name, nav_key) in enumerate(nav_items.items()):
        with cols[i]:
            button_type = "primary" if st.session_state.current_page == nav_key else "secondary"
            if st.button(nav_name, key=f"nav_{nav_key}", use_container_width=True, type=button_type):
                st.session_state.current_page = nav_key
                st.rerun()
    
    # Logout button in last column
    with cols[-1]:
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True, type="secondary"):
            logout()

def show_page_content():
    """Show the content for the current page"""
    if not st.session_state.authenticated:
        return
    
    # Wrap content in styled container
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    
    current_page = st.session_state.current_page
    
    if st.session_state.user_type == "admin":
        require_auth("admin")
        
        if current_page == "dashboard":
            admin_dashboard()
        elif current_page == "rooms":
            room_management()
        elif current_page == "renters":
            renter_management()
        elif current_page == "registrations":
            registration_management()
        elif current_page == "payments":
            payment_management()
        elif current_page == "complaints":
            complaint_management()
        elif current_page == "reports":
            reports()
    else:
        require_auth("renter")
        
        if current_page == "dashboard":
            renter_dashboard()
        elif current_page == "payments":
            my_payments()
        elif current_page == "complaints":
            my_complaints()
        elif current_page == "profile":
            my_profile()
        elif current_page == "notifications":
            notifications()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_footer():
    """Show application footer"""
    st.markdown(f"""
    <div class="footer">
        <h4>🏠 RentNest - Smart Living Management</h4>
        <p>Transforming residential management with intelligent solutions</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
            <div>
                <strong>Version:</strong> 2.0.0<br>
                <strong>Status:</strong> ✅ Online
            </div>
            <div>
                <strong>Support:</strong> 24/7 Available<br>
                <strong>Last Update:</strong> {st.session_state.get('login_time', 'N/A')}
            </div>
        </div>
        <hr style="margin: 1rem 0; border: none; border-top: 1px solid #dee2e6;">
        <small>© 2026 RentNest Solutions. Empowering Smart Living Communities.</small>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Initialize session state
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        # Show login page with new branding
        st.markdown("""
        <div class="top-nav">
            <h1 class="nav-title">🏠 RentNest</h1>
            <p class="nav-subtitle">Smart Living Management Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="content-area">', unsafe_allow_html=True)
        login_page()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Show top navigation
    show_top_navigation()
    
    # Show navigation menu
    show_navigation_menu()
    
    # Show page content
    show_page_content()
    
    # Show footer
    show_footer()

# Run the application
if __name__ == "__main__":
    main()