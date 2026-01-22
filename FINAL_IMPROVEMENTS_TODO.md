# Final Improvements Implementation Guide

## Changes to Implement

### 1. Update Database Schema (simple_database.py)

Add these fields to renters table:
```python
unique_id TEXT UNIQUE NOT NULL,  # Auto-generated unique ID
aadhaar_path TEXT,               # Aadhaar document path
pan_path TEXT,                   # PAN document path
```

Add notifications table:
```python
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

Add complaints table:
```python
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    renter_id INTEGER NOT NULL,
    complaint_type TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'Open',
    submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_date TIMESTAMP,
    admin_response TEXT
)
```

### 2. Update Registration (auth.py)

Add document upload fields:
```python
aadhaar_file = st.file_uploader("Upload Aadhaar Card*", type=['pdf', 'jpg', 'png'])
pan_file = st.file_uploader("Upload PAN Card*", type=['pdf', 'jpg', 'png'])
```

Generate unique ID:
```python
def generate_unique_id():
    timestamp = datetime.now().strftime("%y%m")
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"RN{timestamp}{random_part}"
```

### 3. Update Admin Panel (admin_panel.py)

Remove "Add Renter" tab from renter_management()

Update dashboard to show month-wise income:
```python
def admin_dashboard():
    # Add monthly income chart
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT month_year, SUM(amount) as total
        FROM payments
        GROUP BY month_year
        ORDER BY month_year DESC
        LIMIT 12
    ''')
    monthly_data = cursor.fetchall()
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(x=[m[0] for m in monthly_data], 
               y=[m[1] for m in monthly_data])
    ])
    fig.update_layout(title='Monthly Income')
    st.plotly_chart(fig)
```

Add complaint management:
```python
def complaint_management():
    st.title("📝 Complaint Management")
    
    complaints = db.get_all_complaints()
    
    for complaint in complaints:
        with st.expander(f"#{complaint[0]} - {complaint[1]} - {complaint[4]}"):
            st.write(f"Type: {complaint[2]}")
            st.write(f"Description: {complaint[3]}")
            
            new_status = st.selectbox("Status", ["Open", "In-Progress", "Resolved"])
            admin_response = st.text_area("Response")
            
            if st.button("Update"):
                db.update_complaint(complaint[0], new_status, admin_response)
                # Send notification to renter
                db.create_notification(
                    complaint[1], 'renter',
                    'Complaint Updated',
                    f'Your complaint status: {new_status}'
                )
                st.rerun()
```

### 4. Update Renter Panel (renter_panel.py)

Add notifications page:
```python
def notifications():
    st.title("🔔 Notifications")
    
    notifications = db.get_notifications(st.session_state.user_id, 'renter')
    
    for notif in notifications:
        if not notif[4]:  # is_read
            st.markdown("**🆕 NEW**")
        
        st.info(f"**{notif[1]}**: {notif[2]}")
        st.caption(notif[5])
        
        if not notif[4]:
            if st.button("Mark Read", key=f"read_{notif[0]}"):
                db.mark_notification_read(notif[0])
                st.rerun()
```

Add complaints page:
```python
def my_complaints():
    st.title("📝 My Complaints")
    
    tab1, tab2 = st.tabs(["My Complaints", "Submit New"])
    
    with tab1:
        complaints = db.get_renter_complaints(st.session_state.user_id)
        for c in complaints:
            st.write(f"#{c[0]} - {c[2]} - {c[4]}")
            st.write(c[3])
            if c[7]:
                st.info(f"Admin: {c[7]}")
    
    with tab2:
        with st.form("new_complaint"):
            complaint_type = st.selectbox("Type", 
                ["Water", "Electricity", "Cleaning", "Wi-Fi", "Other"])
            description = st.text_area("Description")
            
            if st.form_submit_button("Submit"):
                db.add_complaint(st.session_state.user_id, 
                               complaint_type, description)
                # Notify admin
                db.create_notification(
                    1, 'admin',
                    'New Complaint',
                    f'New {complaint_type} complaint submitted'
                )
                st.success("Complaint submitted!")
                st.rerun()
```

Make profile updatable:
```python
def my_profile():
    st.title("👤 My Profile")
    
    tab1, tab2 = st.tabs(["View Profile", "Update Profile"])
    
    with tab1:
        # Show current details
        details = db.get_renter_details(st.session_state.user_id)
        st.write(f"Unique ID: {details['unique_id']}")
        st.write(f"Name: {details['name']}")
        # ... other fields
    
    with tab2:
        with st.form("update_profile"):
            new_name = st.text_input("Name", value=current_name)
            new_email = st.text_input("Email", value=current_email)
            
            if st.form_submit_button("Update"):
                db.update_renter_profile(user_id, new_name, new_email)
                # Notify admin
                db.create_notification(
                    1, 'admin',
                    'Profile Updated',
                    f'{current_name} updated their profile'
                )
                st.success("Profile updated! Admin notified.")
                st.rerun()
```

### 5. Update Main.py

Remove sidebar navigation, use only buttons:
```python
def show_navigation_menu():
    if st.session_state.user_type == "admin":
        nav_items = {
            "📊 Dashboard": "dashboard",
            "🏠 Rooms": "rooms",
            "🛏️ Bed Allocation": "allocation",
            "💰 Payments": "payments",
            "📝 Complaints": "complaints",
            "📊 Reports": "reports"
        }
    else:
        nav_items = {
            "🏠 Dashboard": "dashboard",
            "💰 Payments": "payments",
            "📝 Complaints": "complaints",
            "👤 Profile": "profile",
            "🔔 Notifications": "notifications"
        }
    
    cols = st.columns(len(nav_items) + 1)
    
    for i, (name, key) in enumerate(nav_items.items()):
        with cols[i]:
            if st.button(name, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
    
    with cols[-1]:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
```

## Implementation Steps

1. **Update simple_database.py**
   - Add unique_id, aadhaar_path, pan_path to renters table
   - Add notifications table
   - Add complaints table
   - Add helper methods for notifications and complaints

2. **Update auth.py**
   - Add document upload fields
   - Generate unique ID on registration
   - Save uploaded files to uploads/ folder

3. **Update admin_panel.py**
   - Remove "Add Renter" tab
   - Add monthly income chart to dashboard
   - Add complaint management function
   - Add notification viewing

4. **Update renter_panel.py**
   - Add working notifications page
   - Add working complaints page
   - Make profile page updatable
   - Send notifications to admin on updates

5. **Update main.py**
   - Remove sidebar
   - Use only button navigation
   - Clean up UI

## Testing Checklist

- [ ] Registration with documents works
- [ ] Unique ID is generated
- [ ] Documents are saved
- [ ] Notifications work both ways
- [ ] Complaints can be submitted
- [ ] Admin can respond to complaints
- [ ] Profile updates notify admin
- [ ] Monthly income chart shows correctly
- [ ] Navigation buttons work
- [ ] No sidebar appears

## File Upload Handling

```python
import os

def save_uploaded_file(uploaded_file, renter_id, doc_type):
    """Save uploaded file and return path"""
    if uploaded_file:
        # Create uploads directory if not exists
        os.makedirs("uploads", exist_ok=True)
        
        # Generate filename
        ext = uploaded_file.name.split('.')[-1]
        filename = f"{renter_id}_{doc_type}.{ext}"
        filepath = os.path.join("uploads", filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    return None
```

## Database Methods to Add

```python
# In simple_database.py

def create_notification(self, user_id, user_type, title, message):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notifications (user_id, user_type, title, message)
        VALUES (?, ?, ?, ?)
    ''', (user_id, user_type, title, message))
    conn.commit()
    conn.close()

def get_notifications(self, user_id, user_type):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM notifications
        WHERE user_id = ? AND user_type = ?
        ORDER BY created_date DESC
    ''', (user_id, user_type))
    notifications = cursor.fetchall()
    conn.close()
    return notifications

def add_complaint(self, renter_id, complaint_type, description):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO complaints (renter_id, complaint_type, description)
        VALUES (?, ?, ?)
    ''', (renter_id, complaint_type, description))
    conn.commit()
    conn.close()

def update_complaint(self, complaint_id, status, admin_response):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE complaints
        SET status = ?, admin_response = ?, 
            resolved_date = CASE WHEN ? = 'Resolved' THEN CURRENT_TIMESTAMP ELSE NULL END
        WHERE complaint_id = ?
    ''', (status, admin_response, status, complaint_id))
    conn.commit()
    conn.close()
```

---

**Note:** These are the improvements to implement. Each section provides the code structure and logic needed. Implement them one by one and test thoroughly.