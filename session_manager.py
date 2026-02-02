"""
Session Manager - Persistent Login Across Browser Refreshes
Uses Streamlit's built-in session state which persists within the same browser tab
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta


class SessionManager:
    """Manage user sessions with browser persistence"""
    
    SESSION_DIR = Path(".sessions")
    
    @classmethod
    def init(cls):
        """Initialize session storage directory"""
        cls.SESSION_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_session_id(cls) -> str:
        """Get or create unique session ID from browser"""
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id
    
    @classmethod
    def save_login(cls, user_id: int, user_type: str, user_name: str, username: str = None):
        """Save login info to session"""
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.user_type = user_type
        st.session_state.user_name = user_name
        st.session_state.username = username  # for admin
        st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.login_timestamp = datetime.now()
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if user is currently authenticated"""
        # Session persists in Streamlit until user closes browser or explicitly logs out
        return st.session_state.get('authenticated', False)
    
    @classmethod
    def get_user_info(cls) -> dict:
        """Get current user info"""
        if not cls.is_authenticated():
            return None
        
        return {
            'user_id': st.session_state.get('user_id'),
            'user_type': st.session_state.get('user_type'),
            'user_name': st.session_state.get('user_name'),
            'username': st.session_state.get('username'),
            'login_time': st.session_state.get('login_time')
        }
    
    @classmethod
    def clear_session(cls):
        """Clear session (logout)"""
        # Clear all session state keys
        for key in ['authenticated', 'user_id', 'user_type', 'user_name', 
                    'username', 'login_time', 'login_timestamp', 'current_page']:
            if key in st.session_state:
                del st.session_state[key]
    
    @classmethod
    def is_session_valid(cls) -> bool:
        """Check if session is still valid (not expired)"""
        if not cls.is_authenticated():
            return False
        
        login_time = st.session_state.get('login_timestamp')
        if not login_time:
            return False
        
        # Session timeout after 24 hours (can be adjusted)
        session_duration = datetime.now() - login_time
        return session_duration < timedelta(hours=24)
