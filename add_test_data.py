"""
Script to add test data to the PG Management System
Run this to populate the database with sample data for testing
"""

from simple_database import SimplePGDatabase
from datetime import date, timedelta

def add_test_data():
    """Add comprehensive test data to database"""
    db = SimplePGDatabase()
    
    print("🚀 Adding test data to database...")
    print("-" * 50)
    
    # 1. Add Rooms
    print("\n📦 Adding Rooms...")
    rooms_data = [
        ("101", "AC", 3, 8000),
        ("102", "AC", 4, 7000),
        ("103", "Non-AC", 3, 6000),
        ("104", "Non-AC", 4, 5000),
        ("105", "AC", 5, 6500),
        ("106", "Non-AC", 5, 4500),
    ]
    
    for room_number, room_type, sharing, rent in rooms_data:
        success, message = db.add_room(room_number, room_type, sharing, rent)
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ⚠️  {message}")
    
    # 2. Add Renters
    print("\n👥 Adding Renters...")
    renters_data = [
        ("Rahul Kumar", "9876543210", "rahul@email.com", date(2025, 1, 1)),
        ("Priya Sharma", "9876543211", "priya@email.com", date(2025, 1, 5)),
        ("Amit Patel", "9876543212", "amit@email.com", date(2025, 1, 10)),
        ("Sneha Reddy", "9876543213", "sneha@email.com", date(2025, 1, 15)),
        ("Vikram Singh", "9876543214", "vikram@email.com", date(2025, 2, 1)),
        ("Anjali Gupta", "9876543215", "anjali@email.com", date(2025, 2, 5)),
        ("Rajesh Verma", "9876543216", "rajesh@email.com", date(2025, 2, 10)),
        ("Pooja Joshi", "9876543217", "pooja@email.com", date(2025, 2, 15)),
        ("Karan Mehta", "9876543218", "karan@email.com", date(2025, 3, 1)),
        ("Divya Nair", "9876543219", "divya@email.com", date(2025, 3, 5)),
    ]
    
    for name, phone, email, join_date in renters_data:
        success, message = db.add_renter(name, phone, email, join_date)
        if success:
            print(f"  ✅ Added: {name} ({phone})")
        else:
            print(f"  ⚠️  {message}")
    
    # 3. Allocate Beds
    print("\n🛏️  Allocating Beds...")
    bed_allocations = [
        (1, 1, 1),  # Rahul -> Room 101, Bed 1
        (2, 1, 2),  # Priya -> Room 101, Bed 2
        (3, 2, 1),  # Amit -> Room 102, Bed 1
        (4, 2, 2),  # Sneha -> Room 102, Bed 2
        (5, 3, 1),  # Vikram -> Room 103, Bed 1
        (6, 3, 2),  # Anjali -> Room 103, Bed 2
        (7, 4, 1),  # Rajesh -> Room 104, Bed 1
        (8, 4, 2),  # Pooja -> Room 104, Bed 2
    ]
    
    for renter_id, room_id, bed_number in bed_allocations:
        success, message = db.allocate_bed(renter_id, room_id, bed_number)
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ⚠️  {message}")
    
    # 4. Add Payments
    print("\n💰 Adding Payments...")
    
    # Get current date
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
        success, message = db.add_payment(renter_id, month_year, amount, payment_date, method)
        if success:
            print(f"  ✅ Payment recorded: Renter {renter_id} - {month_year} - ₹{amount}")
        else:
            print(f"  ⚠️  {message}")
    
    # 5. Summary
    print("\n" + "=" * 50)
    print("📊 Test Data Summary")
    print("=" * 50)
    
    stats = db.get_dashboard_stats()
    print(f"✅ Total Rooms: {stats['total_rooms']}")
    print(f"✅ Total Beds: {stats['total_beds']}")
    print(f"✅ Occupied Beds: {stats['occupied_beds']}")
    print(f"✅ Empty Beds: {stats['empty_beds']}")
    print(f"✅ Active Renters: {stats['active_renters']}")
    
    # Payment summary
    all_payments = db.get_all_payments()
    total_revenue = sum([p[3] for p in all_payments])
    print(f"✅ Total Payments: {len(all_payments)}")
    print(f"✅ Total Revenue: ₹{total_revenue:,.2f}")
    
    print("\n" + "=" * 50)
    print("🎉 Test data added successfully!")
    print("=" * 50)
    
    print("\n📝 Login Credentials:")
    print("-" * 50)
    print("Admin Login:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nRenter Login (use any phone number):")
    print("  9876543210 (Rahul Kumar)")
    print("  9876543211 (Priya Sharma)")
    print("  9876543212 (Amit Patel)")
    print("  9876543213 (Sneha Reddy)")
    print("  9876543214 (Vikram Singh)")
    print("  9876543215 (Anjali Gupta)")
    print("  9876543216 (Rajesh Verma)")
    print("  9876543217 (Pooja Joshi)")
    print("  9876543218 (Karan Mehta)")
    print("  9876543219 (Divya Nair)")
    print("-" * 50)

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  PG MANAGEMENT SYSTEM - TEST DATA SETUP")
    print("=" * 50)
    
    response = input("\n⚠️  This will add test data to the database. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        add_test_data()
        print("\n✅ Done! You can now run: streamlit run main.py")
    else:
        print("\n❌ Cancelled. No data was added.")