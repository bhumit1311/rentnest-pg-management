import streamlit as st
import pandas as pd
from datetime import datetime, date
from simple_database import SimplePGDatabase
import plotly.express as px
import plotly.graph_objects as go

def admin_dashboard():
    """Simple admin dashboard"""
    st.title("📊 Admin Dashboard")
    
    db = SimplePGDatabase()
    stats = db.get_dashboard_stats()
    
    # Check for unread notifications
    unread_count = db.get_unread_notification_count()
    if unread_count > 0:
        st.warning(f"🔔 You have {unread_count} unread notification{'s' if unread_count > 1 else ''}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rooms", stats['total_rooms'])
    
    with col2:
        st.metric("Total Beds", stats['total_beds'])
    
    with col3:
        st.metric("Occupied Beds", stats['occupied_beds'])
    
    with col4:
        st.metric("Empty Beds", stats['empty_beds'])
    
    st.markdown("---")
    
    # Recent Notifications Section
    st.subheader("🔔 Recent Notifications")
    notifications = db.get_admin_notifications(limit=5)
    
    if notifications:
        for notif in notifications:
            notif_id, notif_type, message, created_date, is_read, renter_name = notif
            
            icon = "📬" if not is_read else "✅"
            bg_color = "#fff3cd" if not is_read else "#f8f9fa"
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: {bg_color}; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #667eea;">
                    {icon} <strong>{notif_type}</strong>: {message}<br>
                    <small>📅 {created_date}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if not is_read:
                    if st.button("Mark Read", key=f"mark_read_{notif_id}"):
                        db.mark_notification_read(notif_id)
                        st.rerun()
        
        if len(notifications) == 5:
            st.info("Showing 5 most recent notifications")
    else:
        st.info("No notifications yet")
    


def room_management():
    """Simple room management"""
    st.title("🏠 Room Management")
    
    db = SimplePGDatabase()
    
    tab1, tab2 = st.tabs(["Add Room", "View Rooms"])
    
    with tab1:
        st.subheader("Add New Room")
        
        with st.form("add_room_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                room_number = st.text_input("Room Number")
                room_type = st.selectbox("Room Type", ["AC", "Non-AC"])
            
            with col2:
                sharing_type = st.selectbox("Sharing Type", [3, 4, 5])
                monthly_rent = st.number_input("Monthly Rent (₹)", min_value=0.0, step=100.0)
            
            submit = st.form_submit_button("➕ Add Room", use_container_width=True, type="primary")
            
            if submit:
                if room_number and monthly_rent > 0:
                    success, message = db.add_room(room_number, room_type, sharing_type, monthly_rent)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please fill in all required fields (Room Number and Monthly Rent)")
    
    with tab2:
        st.subheader("All Rooms")
        rooms = db.get_all_rooms()
        
        if rooms:
            df = pd.DataFrame(rooms, columns=['ID', 'Room Number', 'Type', 'Sharing', 'Rent'])
            df['Rent'] = df['Rent'].apply(lambda x: f'₹{x:,.0f}')
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No rooms added yet")

def renter_management():
    """Simple renter management"""
    st.title("👥 Renter Management")
    
    db = SimplePGDatabase()
    
    tab1, tab2 = st.tabs(["Add Renter", "View Renters"])
    
    with tab1:
        st.subheader("Add New Renter")
        
        with st.form("add_renter_form"):
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email (Optional)")
            join_date = st.date_input("Join Date", value=date.today())
            
            submit = st.form_submit_button("➕ Add Renter", use_container_width=True, type="primary")
            
            if submit:
                if name and phone:
                    success, message = db.add_renter(name, phone, email, join_date)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please fill in all required fields (Name and Phone Number)")
    
    with tab2:
        st.subheader("All Renters")
        renters = db.get_all_renters()
        
        if renters:
            df = pd.DataFrame(renters, columns=['ID', 'Name', 'Phone', 'Email', 'Join Date', 'Active'])
            df['Active'] = df['Active'].map({1: '✅', 0: '❌'})
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No renters added yet")

def registration_management():
    """Bed allocation"""
    st.title("🛏️ Bed Allocation")
    
    db = SimplePGDatabase()
    
    renters = db.get_all_renters()
    rooms = db.get_all_rooms()
    
    if renters and rooms:
        col1, col2 = st.columns(2)
        
        with col1:
            renter_options = {f"{r[1]} ({r[2]})": r[0] for r in renters if r[5]}
            selected_renter = st.selectbox("Select Renter", list(renter_options.keys()))
        
        with col2:
            room_options = {f"Room {r[1]} ({r[2]}, {r[3]}-sharing)": r[0] for r in rooms}
            selected_room = st.selectbox("Select Room", list(room_options.keys()))
        
        if selected_renter and selected_room:
            renter_id = renter_options[selected_renter]
            room_id = room_options[selected_room]
            
            beds = db.get_room_beds(room_id)
            empty_beds = [bed for bed in beds if not bed[2]]
            
            if empty_beds:
                bed_options = {f"Bed {bed[1]}": bed[1] for bed in empty_beds}
                selected_bed = st.selectbox("Select Bed", list(bed_options.keys()))
                
                if st.button("🛏️ Allocate Bed", type="primary", use_container_width=True):
                    bed_number = bed_options[selected_bed]
                    success, message = db.allocate_bed(renter_id, room_id, bed_number)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            else:
                st.warning("⚠️ No empty beds available in this room")
    else:
        if not renters:
            st.info("Add renters first")
        if not rooms:
            st.info("Add rooms first")

def payment_management():
    """Simple payment management"""
    st.title("💰 Payment Management")
    
    db = SimplePGDatabase()
    
    tab1, tab2 = st.tabs(["Record Payment", "Payment History"])
    
    with tab1:
        st.subheader("Record New Payment")
        
        renters = db.get_all_renters()
        renter_options = {}
        
        for renter in renters:
            if renter[5]:  # Active
                details = db.get_renter_details(renter[0])
                if details and details[6]:  # Has room
                    renter_options[f"{details[1]} - Room {details[6]}"] = {
                        'id': renter[0],
                        'rent': details[8] or 0
                    }
        
        if renter_options:
            with st.form("payment_form"):
                selected_renter = st.selectbox("Select Renter", list(renter_options.keys()))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    month_year = st.text_input("Month-Year (YYYY-MM)", 
                                              value=datetime.now().strftime("%Y-%m"))
                    amount = st.number_input("Amount (₹)", 
                                           value=float(renter_options[selected_renter]['rent']),
                                           min_value=0.0, step=100.0)
                
                with col2:
                    payment_date = st.date_input("Payment Date", value=date.today())
                    payment_method = st.selectbox("Payment Method", 
                                                 ["Cash", "UPI", "Bank Transfer", "Card"])
                
                submit = st.form_submit_button("💾 Record Payment", use_container_width=True, type="primary")
                
                if submit:
                    if amount > 0:
                        renter_id = renter_options[selected_renter]['id']
                        success, message = db.add_payment(renter_id, month_year, amount,
                                                         payment_date, payment_method)
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.warning("⚠️ Please enter a valid payment amount")
        else:
            st.info("ℹ️ No renters with room allocation found. Please allocate rooms to renters first.")
    
    with tab2:
        st.subheader("Payment History")
        
        payments = db.get_all_payments()
        
        if payments:
            df = pd.DataFrame(payments, columns=['ID', 'Renter', 'Month', 'Amount', 'Date', 'Method'])
            df['Amount'] = df['Amount'].apply(lambda x: f'₹{x:,.2f}')
            st.dataframe(df, use_container_width=True)
            
            # Simple chart
            total = sum([p[3] for p in payments])
            st.metric("Total Revenue", f"₹{total:,.2f}")
        else:
            st.info("No payments recorded yet")

def complaint_management():
    """Admin complaint management"""
    st.title("📝 Complaint Management")
    
    db = SimplePGDatabase()
    
    # Get complaint statistics
    stats = db.get_complaint_stats()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Complaints", stats['total'])
    
    with col2:
        st.metric("Open", stats['open'], delta=None, delta_color="off")
    
    with col3:
        st.metric("In Progress", stats['in_progress'], delta=None, delta_color="off")
    
    with col4:
        st.metric("Resolved", stats['resolved'], delta=None, delta_color="off")
    
    st.markdown("---")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved"])
    
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    
    with col3:
        filter_category = st.selectbox("Filter by Category", [
            "All", "Maintenance", "Cleanliness", "Electricity",
            "Water Supply", "Security", "Noise", "Room Issues", "Other"
        ])
    
    st.markdown("---")
    
    # Get all complaints
    complaints = db.get_all_complaints()
    
    if complaints:
        # Apply filters
        filtered_complaints = complaints
        
        if filter_status != "All":
            filtered_complaints = [c for c in filtered_complaints if c[5] == filter_status]
        
        if filter_priority != "All":
            filtered_complaints = [c for c in filtered_complaints if c[4] == filter_priority]
        
        if filter_category != "All":
            filtered_complaints = [c for c in filtered_complaints if c[3] == filter_category]
        
        if filtered_complaints:
            st.subheader(f"Complaints ({len(filtered_complaints)})")
            
            # Display complaints
            for complaint in filtered_complaints:
                complaint_id, renter_name, title, category, priority, status, created_date, description, admin_response, resolved_date, phone = complaint
                
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
                    priority_icon = "🔴"
                elif priority == 'Medium':
                    priority_color = "#ffc107"
                    priority_icon = "🟡"
                else:
                    priority_color = "#28a745"
                    priority_icon = "🟢"
                
                with st.expander(f"{status_icon} {priority_icon} [{category}] {title} - {renter_name}", expanded=(status == 'Open')):
                    # Complaint details
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"**Status:** <span style='color: {status_color};'>{status}</span>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"**Priority:** <span style='color: {priority_color};'>{priority}</span>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"**Category:** {category}")
                    with col4:
                        st.markdown(f"**Submitted:** {created_date}")
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**Renter Details:**")
                        st.write(f"👤 {renter_name}")
                        st.write(f"📱 {phone}")
                    
                    with col2:
                        if resolved_date:
                            st.markdown(f"**Resolved on:** {resolved_date}")
                    
                    st.markdown("---")
                    st.markdown("**Description:**")
                    st.write(description)
                    
                    if admin_response:
                        st.markdown("---")
                        st.markdown("**Previous Admin Response:**")
                        st.info(admin_response)
                    
                    # Admin action form
                    if status != 'Resolved':
                        st.markdown("---")
                        st.markdown("**Admin Action:**")
                        
                        with st.form(f"admin_action_{complaint_id}"):
                            new_status = st.selectbox(
                                "Update Status",
                                ["Open", "In Progress", "Resolved"],
                                index=["Open", "In Progress", "Resolved"].index(status),
                                key=f"status_{complaint_id}"
                            )
                            
                            response = st.text_area(
                                "Admin Response",
                                value=admin_response or "",
                                placeholder="Enter your response to the renter...",
                                key=f"response_{complaint_id}"
                            )
                            
                            col1, col2 = st.columns([1, 4])
                            
                            with col1:
                                submit = st.form_submit_button("Update", use_container_width=True)
                            
                            if submit:
                                if response:
                                    success, message = db.update_complaint_status(
                                        complaint_id,
                                        new_status,
                                        response
                                    )
                                    if success:
                                        st.success("✅ " + message)
                                        st.rerun()
                                    else:
                                        st.error("❌ " + message)
                                else:
                                    st.warning("⚠️ Please provide a response")
        else:
            st.info(f"No complaints found matching the selected filters")
    else:
        st.info("📭 No complaints submitted yet")
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <p>When renters submit complaints, they will appear here for review and action.</p>
        </div>
        """, unsafe_allow_html=True)

def reports():
    """Simple reports"""
    st.title("📊 Reports")
    
    db = SimplePGDatabase()
    
    report_type = st.selectbox("Select Report", ["Occupancy", "Renters", "Revenue"])
    
    if report_type == "Occupancy":
        rooms = db.get_all_rooms()
        if rooms:
            data = []
            for room in rooms:
                beds = db.get_room_beds(room[0])
                occupied = sum(1 for bed in beds if bed[2])
                data.append({
                    'Room': room[1],
                    'Type': room[2],
                    'Total Beds': room[3],
                    'Occupied': occupied,
                    'Empty': room[3] - occupied
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
    
    elif report_type == "Renters":
        renters = db.get_all_renters()
        if renters:
            df = pd.DataFrame(renters, columns=['ID', 'Name', 'Phone', 'Email', 'Join Date', 'Active'])
            df['Active'] = df['Active'].map({1: 'Yes', 0: 'No'})
            st.dataframe(df, use_container_width=True)
    
    elif report_type == "Revenue":
        st.subheader("Monthly Revenue Summary")
        
        revenue_records = db.get_all_revenue()
        
        if revenue_records:
            df = pd.DataFrame(revenue_records, columns=['Month', 'Total Revenue', 'Payments', 'Occupancy %', 'Last Updated'])
            df['Total Revenue'] = df['Total Revenue'].apply(lambda x: f'₹{x:,.2f}')
            df['Occupancy %'] = df['Occupancy %'].apply(lambda x: f'{x:.1f}%')
            st.dataframe(df, use_container_width=True)
            
            # Display total revenue across all months
            total = sum([r[1] for r in revenue_records])
            st.metric("Total Revenue (All Time)", f"₹{total:,.2f}")
        else:
            st.info("No revenue data available yet. Revenue data is automatically generated when payments are recorded.")