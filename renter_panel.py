import streamlit as st
import pandas as pd
from datetime import datetime
from simple_database import SimplePGDatabase
import plotly.graph_objects as go

def renter_dashboard():
    """Simple renter dashboard"""
    st.title("🏠 My Dashboard")
    
    db = SimplePGDatabase()
    renter_details = db.get_renter_details(st.session_state.user_id)
    
    if renter_details:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
            <h2>👋 Welcome, {renter_details[1]}!</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if renter_details[6]:
                st.metric("Room Number", renter_details[6])
            else:
                st.metric("Room Status", "Not Allocated")
        
        with col2:
            if renter_details[9]:
                st.metric("Bed Number", renter_details[9])
            else:
                st.metric("Bed Status", "Not Assigned")
        
        with col3:
            if renter_details[8]:
                st.metric("Monthly Rent", f"₹{renter_details[8]:,.0f}")
            else:
                st.metric("Monthly Rent", "TBD")
        
        st.markdown("---")
        
        # Room info
        if renter_details[6]:
            st.subheader("🏠 Room Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"**Room:** {renter_details[6]}")
                st.success(f"**Type:** {renter_details[7]}")
            
            with col2:
                st.success(f"**Bed:** {renter_details[9]}")
                st.success(f"**Rent:** ₹{renter_details[8]:,.0f}/month")
        else:
            st.warning("🏠 Room not allocated yet. Please contact admin.")

def my_payments():
    """Simple payment history"""
    st.title("💰 My Payments")
    
    db = SimplePGDatabase()
    payments = db.get_renter_payments(st.session_state.user_id)
    
    if payments:
        total_paid = sum([p[2] for p in payments])
        st.metric("Total Paid", f"₹{total_paid:,.2f}")
        
        st.markdown("---")
        
        df = pd.DataFrame(payments, columns=['ID', 'Month', 'Amount', 'Date', 'Method'])
        df['Amount'] = df['Amount'].apply(lambda x: f'₹{x:,.2f}')
        
        st.dataframe(df, use_container_width=True)
        
        # Simple chart
        if len(payments) > 1:
            amounts = [p[2] for p in payments]
            months = [p[1] for p in payments]
            
            fig = go.Figure(data=[go.Bar(x=months, y=amounts)])
            fig.update_layout(title='Payment History', xaxis_title='Month', yaxis_title='Amount (₹)')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No payment records found")

def my_complaints():
    """Renter complaint management"""
    st.title("📝 My Complaints")
    
    db = SimplePGDatabase()
    
    tab1, tab2 = st.tabs(["Submit Complaint", "My Complaint History"])
    
    with tab1:
        st.subheader("Submit New Complaint")
        
        with st.form("complaint_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Complaint Title*", placeholder="Brief description of the issue")
                category = st.selectbox("Category*", [
                    "Maintenance",
                    "Cleanliness",
                    "Electricity",
                    "Water Supply",
                    "Security",
                    "Noise",
                    "Room Issues",
                    "Other"
                ])
            
            with col2:
                priority = st.selectbox("Priority*", ["Low", "Medium", "High"])
            
            description = st.text_area("Detailed Description*",
                                      placeholder="Please provide detailed information about your complaint...",
                                      height=150)
            
            submit = st.form_submit_button("Submit Complaint", use_container_width=True)
            
            if submit:
                if title and description and category:
                    success, message = db.add_complaint(
                        st.session_state.user_id,
                        title,
                        description,
                        category,
                        priority
                    )
                    if success:
                        st.success("✅ " + message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ " + message)
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    with tab2:
        st.subheader("My Complaint History")
        
        complaints = db.get_renter_complaints(st.session_state.user_id)
        
        if complaints:
            # Display statistics
            col1, col2, col3 = st.columns(3)
            
            open_count = sum(1 for c in complaints if c[4] == 'Open')
            in_progress_count = sum(1 for c in complaints if c[4] == 'In Progress')
            resolved_count = sum(1 for c in complaints if c[4] == 'Resolved')
            
            with col1:
                st.metric("Open", open_count, delta=None)
            with col2:
                st.metric("In Progress", in_progress_count, delta=None)
            with col3:
                st.metric("Resolved", resolved_count, delta=None)
            
            st.markdown("---")
            
            # Display complaints
            for complaint in complaints:
                complaint_id, title, category, priority, status, created_date, description, admin_response, resolved_date = complaint
                
                # Status color coding
                if status == 'Open':
                    status_color = "#ffc107"
                    status_icon = "🟡"
                elif status == 'In Progress':
                    status_color = "#17a2b8"
                    status_icon = "🔵"
                else:
                    status_color = "#28a745"
                    status_icon = "🟢"
                
                # Priority color coding
                if priority == 'High':
                    priority_color = "#dc3545"
                elif priority == 'Medium':
                    priority_color = "#ffc107"
                else:
                    priority_color = "#28a745"
                
                with st.expander(f"{status_icon} {title} - {category}", expanded=(status != 'Resolved')):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Status:** <span style='color: {status_color};'>{status}</span>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"**Priority:** <span style='color: {priority_color};'>{priority}</span>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"**Submitted:** {created_date}")
                    
                    st.markdown("---")
                    st.markdown("**Description:**")
                    st.write(description)
                    
                    if admin_response:
                        st.markdown("---")
                        st.markdown("**Admin Response:**")
                        st.info(admin_response)
                    
                    if resolved_date:
                        st.markdown(f"**Resolved on:** {resolved_date}")
        else:
            st.info("📭 No complaints submitted yet")
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <p>If you have any issues or concerns, please submit a complaint using the form above.</p>
                <p>We're here to help! 😊</p>
            </div>
            """, unsafe_allow_html=True)

def my_profile():
    """Editable profile view"""
    st.title("👤 My Profile")
    
    db = SimplePGDatabase()
    renter_details = db.get_renter_details(st.session_state.user_id)
    
    if renter_details:
        tab1, tab2 = st.tabs(["View Profile", "Edit Profile"])
        
        with tab1:
            st.subheader("📋 Personal Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {renter_details[1]}")
                st.write(f"**Phone:** {renter_details[2]}")
                st.write(f"**Email:** {renter_details[3] or 'Not provided'}")
            
            with col2:
                st.write(f"**Join Date:** {renter_details[4]}")
                st.write(f"**Status:** {'✅ Active' if renter_details[5] else '❌ Inactive'}")
            
            st.markdown("---")
            st.subheader("🏠 Room Allocation")
            
            if renter_details[6]:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"**Room:** {renter_details[6]}")
                    st.success(f"**Type:** {renter_details[7]}")
                
                with col2:
                    st.success(f"**Bed:** {renter_details[9]}")
                    st.success(f"**Rent:** ₹{renter_details[8]:,.0f}/month")
            else:
                st.warning("🏠 Room not allocated yet. Please contact admin.")
        
        with tab2:
            st.subheader("✏️ Edit Personal Information")
            st.info("📱 Phone number cannot be changed as it's your login ID")
            
            with st.form("edit_profile_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Full Name*", value=renter_details[1])
                
                with col2:
                    new_email = st.text_input("Email", value=renter_details[3] or "")
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    submit = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                
                with col2:
                    cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submit:
                    if new_name:
                        # Check if anything changed
                        if new_name != renter_details[1] or new_email != (renter_details[3] or ""):
                            success, message = db.update_renter_profile(
                                st.session_state.user_id,
                                new_name,
                                new_email if new_email else None
                            )
                            
                            if success:
                                # Add notification for admin
                                notification_msg = f"{new_name} updated their profile"
                                db.add_notification("Profile Update", notification_msg, st.session_state.user_id)
                                
                                st.success(f"✅ {message}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.info("ℹ️ No changes detected")
                    else:
                        st.warning("⚠️ Name is required")
                
                if cancel:
                    st.rerun()

def notifications():
    """Renter notifications view"""
    st.title("🔔 Notifications")
    st.info("ℹ️ Notifications will appear here when admin responds to your complaints or makes important announcements")
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <p>📬 Check your complaints section for admin responses</p>
        <p>💬 All complaint updates are tracked in the complaints tab</p>
    </div>
    """, unsafe_allow_html=True)