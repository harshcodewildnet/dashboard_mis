#!/usr/bin/env python3
"""Test if admin user exists and password works"""

import sys
sys.path.insert(0, '/app')

from api.db import SessionLocal, User
from api.auth import verify_password

db = SessionLocal()
try:
    # Check all users
    users = db.query(User).all()
    print(f"Total users in database: {len(users)}")
    print("="*50)
    
    for user in users:
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Hash (first 50 chars): {user.password_hash[:50]}...")
        
        # Try to verify password
        can_login = verify_password("admin123", user.password_hash)
        print(f"Can login with 'admin123': {can_login}")
        print("-"*50)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
