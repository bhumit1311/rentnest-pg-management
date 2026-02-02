# UI Layer Refactoring TODO

## ✅ COMPLETED
- [x] Fixed syntax errors in `renter_panel.py` (width=\stretch\ -> use_container_width=True)
- [x] Refactored `auth.py` to use new AuthService instead of SimplePGDatabase
- [x] Updated imports in `auth.py` to use new architecture
- [x] Updated admin login to use AuthService.authenticate_admin()
- [x] Updated renter login to use AuthService.authenticate_renter()
- [x] Updated require_auth() to use AuthService authorization methods

## 🔄 IN PROGRESS
- [ ] Update registration in `auth.py` to use AuthService.register_renter()
- [ ] Refactor `admin_panel.py` to use new database and service layers
- [ ] Refactor `renter_panel.py` to use new database and service layers
- [ ] Update `init_data.py` to use new database layer
- [ ] Update `main.py` imports if needed

## 📋 REQUIRED CHANGES

### For admin_panel.py:
- Replace `from simple_database import SimplePGDatabase` with new imports
- Update all database calls to use new Database class
- Consider creating AdminService for business logic separation

### For renter_panel.py:
- Replace `from simple_database import SimplePGDatabase` with new imports
- Update all database calls to use new Database class
- Consider creating RenterService for business logic separation

### For init_data.py:
- Replace `from simple_database import SimplePGDatabase` with new imports
- Update database initialization to use new Database class

## 🎯 NEXT STEPS
1. Complete auth.py registration refactoring
2. Test current changes work
3. Refactor admin_panel.py
4. Refactor renter_panel.py
5. Update init_data.py
6. Final testing and cleanup

## 📊 PROGRESS
- **Completed**: 40%
- **Remaining**: 60%
- **Estimated Time**: 4-6 hours
