import sqlite3
from datetime import datetime

class SimplePGDatabase:
    """Simplified PG Management Database - Only Essential Tables"""
    
    def __init__(self, db_name="pg_simple.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize database with only essential tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. ADMINS TABLE - For admin users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        
        # 2. RENTERS TABLE - For renter users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS renters (
                renter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                join_date DATE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # 3. ROOMS TABLE - For room information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT UNIQUE NOT NULL,
                room_type TEXT NOT NULL,
                sharing_type INTEGER NOT NULL,
                monthly_rent REAL NOT NULL
            )
        ''')
        
        # 4. BEDS TABLE - For bed allocation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS beds (
                bed_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                bed_number INTEGER NOT NULL,
                renter_id INTEGER,
                is_occupied BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (room_id) REFERENCES rooms (room_id),
                FOREIGN KEY (renter_id) REFERENCES renters (renter_id),
                UNIQUE(room_id, bed_number)
            )
        ''')
        
        # 5. PAYMENTS TABLE - For payment records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                renter_id INTEGER NOT NULL,
                month_year TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                FOREIGN KEY (renter_id) REFERENCES renters (renter_id),
                UNIQUE(renter_id, month_year)
            )
        ''')
        
        # 6. COMPLAINTS TABLE - For complaint management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                renter_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                created_date DATETIME NOT NULL,
                resolved_date DATETIME,
                admin_response TEXT,
                FOREIGN KEY (renter_id) REFERENCES renters (renter_id)
            )
        ''')
        
        # 7. NOTIFICATIONS TABLE - For admin notifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_type TEXT NOT NULL,
                message TEXT NOT NULL,
                renter_id INTEGER,
                created_date DATETIME NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY (renter_id) REFERENCES renters (renter_id)
            )
        ''')
        
        # Insert default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM admins WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO admins (username, password, name)
                VALUES ('admin', 'admin123', 'Administrator')
            ''')
        
        conn.commit()
        conn.close()
    
    # ADMIN METHODS
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        conn.close()
        return admin
    
    # RENTER METHODS
    def add_renter(self, name, phone, email, join_date):
        """Add a new renter"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO renters (name, phone, email, join_date)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, email, join_date))
            conn.commit()
            conn.close()
            return True, "Renter added successfully"
        except sqlite3.IntegrityError:
            return False, "Phone number already exists"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def authenticate_renter(self, phone):
        """Authenticate renter user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM renters WHERE phone = ? AND is_active = TRUE", (phone,))
        renter = cursor.fetchone()
        conn.close()
        return renter
    
    def get_all_renters(self):
        """Get all renters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM renters ORDER BY name")
        renters = cursor.fetchall()
        conn.close()
        return renters
    
    def get_renter_details(self, renter_id):
        """Get renter details with room info"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, rm.room_number, rm.room_type, rm.monthly_rent, b.bed_number
            FROM renters r
            LEFT JOIN beds b ON r.renter_id = b.renter_id AND b.is_occupied = TRUE
            LEFT JOIN rooms rm ON b.room_id = rm.room_id
            WHERE r.renter_id = ?
        ''', (renter_id,))
        details = cursor.fetchone()
        conn.close()
        return details
    
    # ROOM METHODS
    def add_room(self, room_number, room_type, sharing_type, monthly_rent):
        """Add a new room with beds"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rooms (room_number, room_type, sharing_type, monthly_rent)
                VALUES (?, ?, ?, ?)
            ''', (room_number, room_type, sharing_type, monthly_rent))
            
            room_id = cursor.lastrowid
            
            # Create beds
            for bed_num in range(1, sharing_type + 1):
                cursor.execute('''
                    INSERT INTO beds (room_id, bed_number)
                    VALUES (?, ?)
                ''', (room_id, bed_num))
            
            conn.commit()
            conn.close()
            return True, f"Room {room_number} added with {sharing_type} beds"
        except sqlite3.IntegrityError:
            return False, f"Room {room_number} already exists"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_all_rooms(self):
        """Get all rooms"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rooms ORDER BY room_number")
        rooms = cursor.fetchall()
        conn.close()
        return rooms
    
    def get_room_beds(self, room_id):
        """Get beds for a room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bed_id, bed_number, is_occupied, renter_id
            FROM beds
            WHERE room_id = ?
            ORDER BY bed_number
        ''', (room_id,))
        beds = cursor.fetchall()
        conn.close()
        return beds
    
    # BED ALLOCATION
    def allocate_bed(self, renter_id, room_id, bed_number):
        """Allocate a bed to a renter"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if bed is available
            cursor.execute('''
                SELECT is_occupied FROM beds
                WHERE room_id = ? AND bed_number = ?
            ''', (room_id, bed_number))
            
            bed = cursor.fetchone()
            if not bed or bed[0]:
                return False, "Bed is not available"
            
            # Check if renter already has a bed
            cursor.execute("SELECT COUNT(*) FROM beds WHERE renter_id = ?", (renter_id,))
            if cursor.fetchone()[0] > 0:
                return False, "Renter already has a bed"
            
            # Allocate bed
            cursor.execute('''
                UPDATE beds
                SET is_occupied = TRUE, renter_id = ?
                WHERE room_id = ? AND bed_number = ?
            ''', (renter_id, room_id, bed_number))
            
            conn.commit()
            conn.close()
            return True, "Bed allocated successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    # PAYMENT METHODS
    def add_payment(self, renter_id, month_year, amount, payment_date, payment_method):
        """Add a payment record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payments (renter_id, month_year, amount, payment_date, payment_method)
                VALUES (?, ?, ?, ?, ?)
            ''', (renter_id, month_year, amount, payment_date, payment_method))
            conn.commit()
            conn.close()
            return True, "Payment recorded successfully"
        except sqlite3.IntegrityError:
            return False, f"Payment for {month_year} already exists"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_renter_payments(self, renter_id):
        """Get payment history for a renter"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT payment_id, month_year, amount, payment_date, payment_method
            FROM payments
            WHERE renter_id = ?
            ORDER BY payment_date DESC
        ''', (renter_id,))
        payments = cursor.fetchall()
        conn.close()
        return payments
    
    def get_all_payments(self):
        """Get all payments"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.payment_id, r.name, p.month_year, p.amount, p.payment_date, p.payment_method
            FROM payments p
            JOIN renters r ON p.renter_id = r.renter_id
            ORDER BY p.payment_date DESC
        ''')
        payments = cursor.fetchall()
        conn.close()
        return payments
    
    # DASHBOARD STATS
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM rooms")
        total_rooms = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM beds")
        total_beds = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM beds WHERE is_occupied = TRUE")
        occupied_beds = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM renters WHERE is_active = TRUE")
        active_renters = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_rooms': total_rooms,
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'empty_beds': total_beds - occupied_beds,
            'active_renters': active_renters
        }
# COMPLAINT METHODS
    def add_complaint(self, renter_id, title, description, category, priority='Medium'):
        """Add a new complaint"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO complaints (renter_id, title, description, category, priority, status, created_date)
                VALUES (?, ?, ?, ?, ?, 'Open', ?)
            ''', (renter_id, title, description, category, priority, created_date))
            conn.commit()
            conn.close()
            return True, "Complaint submitted successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_all_complaints(self):
        """Get all complaints with renter details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.complaint_id, r.name, c.title, c.category, c.priority, c.status, 
                   c.created_date, c.description, c.admin_response, c.resolved_date, r.phone
            FROM complaints c
            JOIN renters r ON c.renter_id = r.renter_id
            ORDER BY 
                CASE c.status 
                    WHEN 'Open' THEN 1 
                    WHEN 'In Progress' THEN 2 
                    WHEN 'Resolved' THEN 3 
                END,
                CASE c.priority 
                    WHEN 'High' THEN 1 
                    WHEN 'Medium' THEN 2 
                    WHEN 'Low' THEN 3 
                END,
                c.created_date DESC
        ''')
        complaints = cursor.fetchall()
        conn.close()
        return complaints
    
    def get_renter_complaints(self, renter_id):
        """Get complaints for a specific renter"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT complaint_id, title, category, priority, status, created_date, 
                   description, admin_response, resolved_date
            FROM complaints
            WHERE renter_id = ?
            ORDER BY created_date DESC
        ''', (renter_id,))
        complaints = cursor.fetchall()
        conn.close()
        return complaints
    
    def update_complaint_status(self, complaint_id, status, admin_response=None):
        """Update complaint status and add admin response"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if status == 'Resolved':
                resolved_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    UPDATE complaints
                    SET status = ?, admin_response = ?, resolved_date = ?
                    WHERE complaint_id = ?
                ''', (status, admin_response, resolved_date, complaint_id))
            else:
                cursor.execute('''
                    UPDATE complaints
                    SET status = ?, admin_response = ?
                    WHERE complaint_id = ?
                ''', (status, admin_response, complaint_id))
            
            conn.commit()
            conn.close()
            return True, "Complaint updated successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_complaint_stats(self):
        """Get complaint statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Open'")
        open_complaints = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
        in_progress = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
        resolved = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'open': open_complaints,
            'in_progress': in_progress,
            'resolved': resolved,
            'total': total
        }
    
    def update_renter_profile(self, renter_id, name, email):
        """Update renter profile information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE renters
                SET name = ?, email = ?
                WHERE renter_id = ?
            ''', (name, email, renter_id))
            conn.commit()
            conn.close()
            return True, "Profile updated successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    # NOTIFICATION METHODS
    def add_notification(self, notification_type, message, renter_id=None):
        """Add a notification for admin"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO notifications (notification_type, message, renter_id, created_date, is_read)
                VALUES (?, ?, ?, ?, 0)
            ''', (notification_type, message, renter_id, created_date))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def get_admin_notifications(self, limit=50):
        """Get admin notifications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT n.notification_id, n.notification_type, n.message, n.created_date, 
                   n.is_read, r.name as renter_name
            FROM notifications n
            LEFT JOIN renters r ON n.renter_id = r.renter_id
            ORDER BY n.is_read ASC, n.created_date DESC
            LIMIT ?
        ''', (limit,))
        notifications = cursor.fetchall()
        conn.close()
        return notifications
    
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications
                SET is_read = 1
                WHERE notification_id = ?
            ''', (notification_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def get_unread_notification_count(self):
        """Get count of unread notifications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read = 0")
        count = cursor.fetchone()[0]
        conn.close()
        return count