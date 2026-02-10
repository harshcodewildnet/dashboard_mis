#!/usr/bin/env python3
"""Simple script to add admin user"""

import sys
sys.path.insert(0, '/app')

from api.db import SessionLocal, User, Department
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
try:
    # Clear existing users
    db.query(User).delete()
    db.commit()
    print("Cleared existing users")
    
    # Add admin user
    admin_hash = pwd_context.hash("admin123")
    print(f"Generated hash for admin123: {admin_hash[:50]}...")
    
    admin = User(
        email="admin@company.com",
        password_hash=admin_hash,
        role="ADMIN",
        department_key=None,
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("✓ Created admin user: admin@company.com")
    
    # Verify it was created
    check = db.query(User).filter(User.email == "admin@company.com").first()
    if check:
        print(f"✓ User verified in database")
        print(f"  Email: {check.email}")
        print(f"  Role: {check.role}")
    else:
        print("✗ ERROR: User not found after creation!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\nDone! Try logging in with admin@company.com / admin123")
