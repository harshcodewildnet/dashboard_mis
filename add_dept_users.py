#!/usr/bin/env python3
"""Add department head user for RBAC testing"""

import sys
sys.path.insert(0, '/app')

from api.db import SessionLocal, User, Department
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
try:
    # Add departments if they don't exist
    depts = [
        {'k': 'DM', 'n': 'Digital Marketing', 'c': 'Digital Marketing'},
        {'k': 'OH', 'n': 'Overhead', 'c': 'Overhead'}
    ]
    
    for d in depts:
        existing = db.query(Department).filter(Department.department_key == d['k']).first()
        if not existing:
            dept = Department(
                department_key=d['k'],
                department_name=d['n'],
                cost_centre_parent=d['c']
            )
            db.add(dept)
            print(f"✓ Created department: {d['n']}")
        else:
            print(f"  Department already exists: {d['n']}")
    
    db.commit()
    
    # Add department head user
    existing_dm = db.query(User).filter(User.email == "dm@company.com").first()
    if not existing_dm:
        dm_hash = pwd_context.hash("dm123")
        dm_user = User(
            email="dm@company.com",
            password_hash=dm_hash,
            role="DEPT_HEAD",
            department_key="DM",
            is_active=True
        )
        db.add(dm_user)
        db.commit()
        print("✓ Created department head user: dm@company.com / dm123")
    else:
        print("  Department head user already exists")
        
    # List all users
    print("\n" + "="*60)
    print("ALL USERS:")
    print("="*60)
    users = db.query(User).all()
    for user in users:
        print(f"  {user.email} - {user.role} - Dept: {user.department_key or 'ALL'}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
