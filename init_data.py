"""
Auto-initialize database with test data on app startup
This ensures data is available even after Streamlit Cloud restarts
"""

from simple_database import SimplePGDatabase
from datetime import date, timedelta

def initialize_database():
    """Initialize database with test data if empty"""
    db = SimplePGDatabase()
    
    # Check if data already exists
    rooms = db.get_all_rooms()
    if rooms:
        return  # Data already exists, skip initialization
    
    print("🚀 Initializing database with test data...")
    
    # 1. Add Rooms
    rooms_data = [
        ("101", "AC", 3, 8000),
        ("102", "AC", 4, 7000),
        ("103", "Non-AC", 3, 6000),
        ("104", "Non-AC", 4, 5000),
        ("105", "AC", 5, 6500),
        ("106", "Non-AC", 5, 4500),
    ]
    
    for room_number, room_type, sharing, rent in rooms_data:
        db.add_room(room_number, room_type, sharing, rent)
    
    # 2. Add Renters
    renters_data = [
        ("Rahul Kumar", "9876543210", "rahul@email.com", date(2025, 1, 1)),
        ("Arjun Sharma", "9876543211", "arjun@email.com", date(2025, 1, 5)),
        ("Amit Patel", "9876543212", "amit@email.com", date(2025, 1, 10)),
        ("Rohan Reddy", "9876543213", "rohan@email.com", date(2025, 1, 15)),
        ("Vikram Singh", "9876543214", "vikram@email.com", date(2025, 2, 1)),
        ("Aditya Gupta", "9876543215", "aditya@email.com", date(2025, 2, 5)),
        ("Rajesh Verma", "9876543216", "rajesh@email.com", date(2025, 2, 10)),
        ("Sanjay Joshi", "9876543217", "sanjay@email.com", date(2025, 2, 15)),
        ("Karan Mehta", "9876543218", "karan@email.com", date(2025, 3, 1)),
        ("Nikhil Nair", "9876543219", "nikhil@email.com", date(2025, 3, 5)),
    ]
    
    for name, phone, email, join_date in renters_data:
        db.add_renter(name, phone, email, join_date)
    
    # 3. Allocate Beds
    bed_allocations = [
        (1, 1, 1),  # Rahul -> Room 101, Bed 1
        (2, 1, 2),  # Arjun -> Room 101, Bed 2
        (3, 2, 1),  # Amit -> Room 102, Bed 1
        (4, 2, 2),  # Rohan -> Room 102, Bed 2
        (5, 3, 1),  # Vikram -> Room 103, Bed 1
        (6, 3, 2),  # Aditya -> Room 103, Bed 2
        (7, 4, 1),  # Rajesh -> Room 104, Bed 1
        (8, 4, 2),  # Sanjay -> Room 104, Bed 2
    ]
    
    for renter_id, room_id, bed_number in bed_allocations:
        db.allocate_bed(renter_id, room_id, bed_number)
    
    # 4. Add Payments
    today = date.today()
    current_month = today.strftime("%Y-%m")
    last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    two_months_ago = (today.replace(day=1) - timedelta(days=32)).strftime("%Y-%m")
    
    payments_data = [
        # Current month payments
        (1, current_month, 8000, today, "UPI"),
        (2, current_month, 8000, today, "Cash"),
        (3, current_month, 7000, today, "Bank Transfer"),
        (5, current_month, 6000, today, "UPI"),
        (7, current_month, 5000, today, "Cash"),
        
        # Last month payments
        (1, last_month, 8000, today - timedelta(days=30), "UPI"),
        (2, last_month, 8000, today - timedelta(days=30), "Cash"),
        (3, last_month, 7000, today - timedelta(days=30), "Bank Transfer"),
        (4, last_month, 7000, today - timedelta(days=30), "UPI"),
        (5, last_month, 6000, today - timedelta(days=30), "Cash"),
        (6, last_month, 6000, today - timedelta(days=30), "UPI"),
        (7, last_month, 5000, today - timedelta(days=30), "Bank Transfer"),
        (8, last_month, 5000, today - timedelta(days=30), "Cash"),
        
        # Two months ago payments
        (1, two_months_ago, 8000, today - timedelta(days=60), "UPI"),
        (2, two_months_ago, 8000, today - timedelta(days=60), "Cash"),
        (3, two_months_ago, 7000, today - timedelta(days=60), "Bank Transfer"),
        (5, two_months_ago, 6000, today - timedelta(days=60), "UPI"),
    ]
    
    for renter_id, month_year, amount, payment_date, method in payments_data:
        db.add_payment(renter_id, month_year, amount, payment_date, method)
    
    print("✅ Database initialized with test data!")