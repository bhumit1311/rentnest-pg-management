#!/usr/bin/env python3
"""Fix broken width parameters in Streamlit files"""

# Read admin_panel.py and fix all broken lines
with open('admin_panel.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the broken width=" stretch\ patterns
content = content.replace(', width=" stretch\\)', ')')

with open('admin_panel.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Do the same for renter_panel.py
with open('renter_panel.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(', width=" stretch\\)', ')')

with open('renter_panel.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Fixed all broken width parameters')

