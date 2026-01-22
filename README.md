# 🏠 Simple PG Management System

A streamlined and easy-to-use PG (Paying Guest) management system built with Streamlit.

## 📋 Features

### Admin Features
- **Dashboard** - View occupancy statistics with charts
- **Room Management** - Add and manage rooms with rent
- **Renter Management** - Add and manage renters
- **Bed Allocation** - Assign beds to renters
- **Payment Management** - Record and track payments with auto-fill
- **Reports** - Interactive occupancy, revenue, and renter reports

### Renter Features
- **Registration** - Self-registration with phone number
- **Dashboard** - View room and payment information
- **My Payments** - View payment history with charts
- **My Profile** - View personal and room details

## 🗄️ Database Structure

Simple database with only 5 essential tables:

1. **admins** - Admin users
2. **renters** - Renter information (name, phone, email, join date)
3. **rooms** - Room details (number, type, sharing, rent)
4. **beds** - Bed allocation (room, bed number, renter)
5. **payments** - Payment records (renter, month, amount, date, method)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Test Data (Optional but Recommended)
```bash
python add_test_data.py
```
This will create:
- 6 rooms (AC and Non-AC)
- 10 renters
- 8 bed allocations
- 17 payment records

### 3. Run the Application
```bash
streamlit run main.py
```

## 🔐 Login Credentials

### Admin Login
- **Username:** `admin`
- **Password:** `admin123`

### Renter Login (After adding test data)
Use any of these phone numbers:
- `9876543210` - Rahul Kumar
- `9876543211` - Priya Sharma
- `9876543212` - Amit Patel
- `9876543213` - Sneha Reddy
- `9876543214` - Vikram Singh
- `9876543215` - Anjali Gupta
- `9876543216` - Rajesh Verma
- `9876543217` - Pooja Joshi
- `9876543218` - Karan Mehta
- `9876543219` - Divya Nair

### New Renter Registration
- Click on "Register as Renter" tab
- Fill in your details
- Contact admin for approval

## 📊 Technologies

- **Streamlit** - Web framework
- **SQLite** - Database
- **Pandas** - Data handling
- **Plotly** - Interactive charts and visualizations

## 📁 Project Structure

```
pg-management/
├── main.py              # Main application
├── simple_database.py   # Database operations (5 tables only)
├── auth.py             # Authentication & Registration
├── admin_panel.py      # Admin interface
├── renter_panel.py     # Renter interface
├── add_test_data.py    # Script to add sample data
├── requirements.txt    # Dependencies (only 3!)
├── README.md          # This file
└── pg_simple.db       # SQLite database (auto-created)
```

## 💡 Usage Guide

### For Admins

#### 1. Add Rooms
- Go to **Rooms** → **Add Room**
- Enter room number, type (AC/Non-AC), sharing (3/4/5), and monthly rent
- Beds are created automatically based on sharing type

#### 2. Add Renters (or they can self-register)
- Go to **Renters** → **Add Renter**
- Enter name, phone, email, and join date
- Renter can now login with their phone number

#### 3. Allocate Beds
- Go to **Registrations** (Bed Allocation)
- Select renter and room
- Choose available bed
- Click "Allocate Bed"

#### 4. Record Payments
- Go to **Payments** → **Record Payment**
- Select renter (rent amount auto-fills from room allocation)
- Enter month-year (format: YYYY-MM)
- Select payment date and method
- Click "Record Payment"

#### 5. View Reports
- Go to **Reports**
- Choose report type:
  - **Occupancy** - See bed occupancy with interactive charts
  - **Revenue** - View payment trends and monthly revenue
  - **Renters** - List all renters with details

### For Renters

#### 1. Register
- Click **Register as Renter** tab on login page
- Fill in your details (name, phone, email)
- Wait for admin approval

#### 2. Login
- Use your registered phone number
- View your dashboard

#### 3. View Dashboard
- See your room allocation
- Check monthly rent
- View bed number

#### 4. Check Payments
- Go to **My Payments**
- View payment history
- See total paid amount
- View payment chart

#### 5. View Profile
- Go to **My Profile**
- See personal information
- View room allocation details

## 🎨 Features Highlights

### Interactive Charts
- Pie charts for occupancy distribution
- Bar charts for room-wise occupancy
- Line charts for revenue trends
- Payment history visualizations

### Auto-Fill Features
- Rent amount auto-fills based on room allocation
- Current month auto-fills in payment form
- Join date defaults to today

### Smart Validations
- Duplicate phone number prevention
- Duplicate payment prevention (same renter + month)
- Bed availability checking
- Active renter verification

## 🔧 Customization

### Change Admin Password
Edit `simple_database.py` line 48:
```python
VALUES ('admin', 'your_new_password', 'Administrator')
```

### Modify Rent Amounts
Update when adding rooms or edit database directly

### Add More Fields
Modify `simple_database.py` table schemas as needed

## 📝 Test Data Summary

After running `add_test_data.py`:
- ✅ 6 Rooms (3 AC, 3 Non-AC)
- ✅ 24 Total Beds
- ✅ 10 Renters
- ✅ 8 Occupied Beds
- ✅ 16 Empty Beds
- ✅ 17 Payment Records
- ✅ ₹115,000 Total Revenue

## 🐛 Troubleshooting

### Database Issues
- Delete `pg_simple.db` and restart the app
- Run `add_test_data.py` again to repopulate

### Login Issues
- Verify phone number is registered
- Check if renter account is active
- For admin, use exact credentials

### Payment Recording Fails
- Ensure renter has room allocation
- Check for duplicate month-year entry
- Verify amount is greater than 0

## 📞 Support

For issues or questions:
- Check code comments in files
- Review this README
- Contact system administrator

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Run test data script
3. ✅ Start the application
4. ✅ Login as admin
5. ✅ Explore features
6. ✅ Add your own data

## 📄 License

Free to use and modify for your needs.

---

**Version:** 2.0 Simple  
**Last Updated:** January 21, 2026  
**Status:** ✅ Production Ready with Test Data

**Quick Commands:**
```bash
# Install
pip install -r requirements.txt

# Add test data
python add_test_data.py

# Run app
streamlit run main.py
```

🎉 **Enjoy your simplified PG Management System!**