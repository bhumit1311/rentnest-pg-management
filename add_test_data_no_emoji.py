"""
Script to add test data to the PG Management System
Run this to populate the database with sample data for testing
"""

from datetime import date, timedelta, datetime
from db.database import Database, DatabaseInitializer
from utils import PasswordHasher


def add_test_data():
    """Add comprehensive test data using the project's main Database."""
    db = Database()
    initializer = DatabaseInitializer(db)
    initializer.initialize_schema()
    initializer.create_default_admin()

    ph = PasswordHasher()

    print("Adding test data to main database...")
    print("-" * 50)

    # 1. Add Rooms
    print("\nAdding Rooms...")
    rooms_data = [
        ("101", "AC", 3, 8000),
        ("102", "AC", 4, 7000),
        ("103", "Non-AC", 3, 6000),
        ("104", "Non-AC", 4, 5000),
        ("105", "AC", 5, 6500),
        ("106", "Non-AC", 5, 4500),
        ("201", "AC", 3, 8500),
        ("202", "Non-AC", 4, 5500),
    ]

    room_ids = []
    for room_number, room_type, sharing, rent in rooms_data:
        try:
            room_id = db.execute_query(
                "INSERT INTO rooms (room_number, room_type, sharing_type, monthly_rent) VALUES (?, ?, ?, ?)",
                (room_number, room_type, sharing, rent)
            )
            # create beds for room
            for bed_num in range(1, sharing + 1):
                db.execute_query(
                    "INSERT INTO beds (room_id, bed_number) VALUES (?, ?)",
                    (room_id, bed_num)
                )
            room_ids.append(room_id)
            print(f"  [SUCCESS] Room {room_number} (id={room_id}) added")
        except Exception as e:
            print(f"  [WARNING] Could not add room {room_number}: {e}")

    # 2. Add Renters
    print("\nAdding Renters...")
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
        ("Deepak Pawar", "9876543220", "deepak@email.com", date(2025, 3, 10)),
        ("Gaurav Rana", "9876543221", "gaurav@email.com", date(2025, 3, 15)),
        ("Harish Rawat", "9876543222", "harish@email.com", date(2025, 4, 1)),
        ("Inder Singh", "9876543223", "inder@email.com", date(2025, 4, 5)),
        ("Jatin Kumar", "9876543224", "jatin@email.com", date(2025, 4, 10)),
        ("Kapil Dev", "9876543225", "kapil@email.com", date(2025, 4, 15)),
        ("Lalit Modi", "9876543226", "lalit@email.com", date(2025, 5, 1)),
        ("Manish Pandey", "9876543227", "manish@email.com", date(2025, 5, 5)),
        ("Neeraj Chopra", "9876543228", "neeraj@email.com", date(2025, 5, 10)),
        ("Pankaj Tripathi", "9876543229", "pankaj@email.com", date(2025, 5, 15)),
    ]

    renter_ids = []
    for name, phone, email, join_date in renters_data:
        try:
            renter_id = db.execute_query(
                "INSERT INTO renters (name, phone, email, join_date) VALUES (?, ?, ?, ?)",
                (name, phone, email, join_date.isoformat())
            )
            renter_ids.append(renter_id)
            print(f"  [SUCCESS] Added: {name} (id={renter_id})")
        except Exception as e:
            print(f"  [WARNING] Could not add renter {name}: {e}")

    # 3. Allocate Beds (use existing room ids/beds)
    print("\nAllocating Beds...")
    bed_allocations = [
        (1, 1, 1),  # Rahul -> Room 101, Bed 1
        (2, 1, 2),  # Arjun -> Room 101, Bed 2
        (3, 2, 1),  # Amit -> Room 102, Bed 1
        (4, 2, 2),  # Rohan -> Room 102, Bed 2
        (5, 3, 1),  # Vikram -> Room 103, Bed 1
        (6, 3, 2),  # Aditya -> Room 103, Bed 2
        (7, 4, 1),  # Rajesh -> Room 104, Bed 1
        (8, 4, 2),  # Sanjay -> Room 104, Bed 2
        (9, 5, 1),  # Karan -> Room 105, Bed 1
        (10, 5, 2), # Nikhil -> Room 105, Bed 2
        (11, 6, 1), # Deepak -> Room 106, Bed 1
        (12, 6, 2), # Gaurav -> Room 106, Bed 2
        (13, 7, 1), # Harish -> Room 201, Bed 1
        (14, 7, 2), # Inder -> Room 201, Bed 2
        (15, 8, 1), # Jatin -> Room 202, Bed 1
        (16, 8, 2), # Kapil -> Room 202, Bed 2
    ]

    for renter_id, room_index, bed_number in bed_allocations:
        try:
            # rooms_data order corresponds to room indices 1..len(rooms_data)
            room_id = room_index  # because we inserted rooms sequentially and their ids will match insertion order
            db.execute_query(
                "UPDATE beds SET is_occupied = 1, renter_id = ?, occupied_since = ? WHERE room_id = ? AND bed_number = ? AND is_occupied = 0",
                (renter_id, datetime.now().date().isoformat(), room_id, bed_number)
            )
            print(f"  [SUCCESS] Allocated renter {renter_id} to room_id {room_id} bed {bed_number}")
        except Exception as e:
            print(f"  [WARNING] Could not allocate bed for renter {renter_id}: {e}")

    # 4. Add Payments
    print("\nAdding Payments...")
    today = date.today()
    current_month = today.strftime("%Y-%m")
    last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    two_months_ago = (today.replace(day=1) - timedelta(days=32)).strftime("%Y-%m")

    payments_data = [
        (1, current_month, 8000, today.isoformat(), "UPI"),
        (2, current_month, 8000, today.isoformat(), "Cash"),
        (3, current_month, 7000, today.isoformat(), "Bank Transfer"),
        (5, current_month, 6000, today.isoformat(), "UPI"),
        (7, current_month, 5000, today.isoformat(), "Cash"),
        (1, last_month, 8000, (today - timedelta(days=30)).isoformat(), "UPI"),
        (2, last_month, 8000, (today - timedelta(days=30)).isoformat(), "Cash"),
        (3, last_month, 7000, (today - timedelta(days=30)).isoformat(), "Bank Transfer"),
        (4, last_month, 7000, (today - timedelta(days=30)).isoformat(), "UPI"),
        (5, last_month, 6000, (today - timedelta(days=30)).isoformat(), "Cash"),
        (6, last_month, 6000, (today - timedelta(days=30)).isoformat(), "UPI"),
        (7, last_month, 5000, (today - timedelta(days=30)).isoformat(), "Bank Transfer"),
        (8, last_month, 5000, (today - timedelta(days=30)).isoformat(), "Cash"),
        (1, two_months_ago, 8000, (today - timedelta(days=60)).isoformat(), "UPI"),
        (2, two_months_ago, 8000, (today - timedelta(days=60)).isoformat(), "Cash"),
        (3, two_months_ago, 7000, (today - timedelta(days=60)).isoformat(), "Bank Transfer"),
        (5, two_months_ago, 6000, (today - timedelta(days=60)).isoformat(), "UPI"),
    ]

    for renter_id, month_year, amount, payment_date, method in payments_data:
        try:
            db.execute_query(
                "INSERT OR IGNORE INTO payments (renter_id, month_year, amount, payment_date, payment_method) VALUES (?, ?, ?, ?, ?)",
                (renter_id, month_year, amount, payment_date, method)
            )
            print(f"  [SUCCESS] Payment recorded: Renter {renter_id} - {month_year} - {amount}")
        except Exception as e:
            print(f"  [WARNING] Could not record payment for renter {renter_id}: {e}")

    # 5. Summary
    print("\n" + "=" * 50)
    print("Test Data Summary")
    print("=" * 50)

    stats = {
        'total_rooms': db.execute_query("SELECT COUNT(*) as count FROM rooms", fetch_one=True)['count'],
        'total_beds': db.execute_query("SELECT COUNT(*) as count FROM beds", fetch_one=True)['count'],
        'occupied_beds': db.execute_query("SELECT COUNT(*) as count FROM beds WHERE is_occupied = 1", fetch_one=True)['count'],
        'active_renters': db.execute_query("SELECT COUNT(*) as count FROM renters WHERE is_active = 1", fetch_one=True)['count']
    }

    print(f"Total Rooms: {stats['total_rooms']}")
    print(f"Total Beds: {stats['total_beds']}")
    print(f"Occupied Beds: {stats['occupied_beds']}")
    print(f"Empty Beds: {stats['total_beds'] - stats['occupied_beds']}")
    print(f"Active Renters: {stats['active_renters']}")

    all_payments = db.execute_query(
        '''SELECT p.payment_id, r.name, p.month_year, p.amount, p.payment_date, p.payment_method
           FROM payments p JOIN renters r ON p.renter_id = r.renter_id''',
        fetch_all=True
    )
    total_revenue = sum([p['amount'] for p in all_payments]) if all_payments else 0
    print(f"Total Payments: {len(all_payments) if all_payments else 0}")
    print(f"Total Revenue: {total_revenue:,.2f}")

    print("\n" + "=" * 50)
    print("Test data added successfully!")
    print("=" * 50)

    print("\nLogin Credentials:")
    print("-" * 50)
    print("Admin Login:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nRenter Login (use any phone number):")
    for name, phone, *_ in renters_data[:10]:
        print(f"  {phone} ({name})")
    print("-" * 50)

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  PG MANAGEMENT SYSTEM - TEST DATA SETUP")
    print("=" * 50)
    
    response = input("\nThis will add test data to the database. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        add_test_data()
        print("\n[SUCCESS] Done! You can now run: streamlit run main.py")
    else:
        print("\n[CANCELLED] No data was added.")
