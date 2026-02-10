#!/usr/bin/env python3
"""Add all 6 departments and create users for each"""

import sys
sys.path.insert(0, '/app')

from api.db import SessionLocal, User, Department
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
try:
    print("="*60)
    print("ADDING ALL DEPARTMENTS AND USERS")
    print("="*60)
    
    # Define all 6 departments
    departments_data = [
        {'k': 'DM', 'n': 'Digital Marketing', 'c': 'Digital Marketing'},
        {'k': 'INT_DM', 'n': 'International D M', 'c': 'International D M'},
        {'k': 'PPC', 'n': 'PPC', 'c': 'PPC'},
        {'k': 'SA', 'n': 'Staff Augmentation', 'c': 'Staff Augmentation'},
        {'k': 'OH', 'n': 'Overhead', 'c': 'Overhead'},
        {'k': 'WE', 'n': 'Wildnet Edge', 'c': 'Wildnet Edge'}
    ]
    
    # Add departments
    print("\n[1/2] Adding Departments...")
    print("-"*60)
    for d in departments_data:
        existing = db.query(Department).filter(Department.department_key == d['k']).first()
        if not existing:
            dept = Department(
                department_key=d['k'],
                department_name=d['n'],
                cost_centre_parent=d['c']
            )
            db.add(dept)
            print(f"  ✓ Created: {d['n']} ({d['k']})")
        else:
            print(f"  - Already exists: {d['n']} ({d['k']})")
    
    db.commit()
    print(f"\n  Total departments in DB: {db.query(Department).count()}")
    
    # Define department users (one for each department)
    users_data = [
        {'e': 'dm@company.com', 'p': 'dm123', 'r': 'DEPT_HEAD', 'd': 'DM'},
        {'e': 'int_dm@company.com', 'p': 'intdm123', 'r': 'DEPT_HEAD', 'd': 'INT_DM'},
        {'e': 'ppc@company.com', 'p': 'ppc123', 'r': 'DEPT_HEAD', 'd': 'PPC'},
        {'e': 'sa@company.com', 'p': 'sa123', 'r': 'DEPT_HEAD', 'd': 'SA'},
        {'e': 'oh@company.com', 'p': 'oh123', 'r': 'DEPT_HEAD', 'd': 'OH'},
        {'e': 'we@company.com', 'p': 'we123', 'r': 'DEPT_HEAD', 'd': 'WE'}
    ]
    
    # Add users
    print("\n[2/2] Adding Department Users...")
    print("-"*60)
    for u in users_data:
        existing = db.query(User).filter(User.email == u['e']).first()
        if not existing:
            hashed = pwd_context.hash(u['p'])
            user = User(
                email=u['e'],
                password_hash=hashed,
                role=u['r'],
                department_key=u['d'],
                is_active=True
            )
            db.add(user)
            print(f"  ✓ Created: {u['e']} (Dept: {u['d']}, Password: {u['p']})")
        else:
            print(f"  - Already exists: {u['e']}")
    
    db.commit()
    print(f"\n  Total users in DB: {db.query(User).count()}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY - ALL USERS")
    print("="*60)
    users = db.query(User).all()
    print(f"\n{'Email':<25} {'Role':<12} {'Department'}")
    print("-"*60)
    for user in users:
        dept = user.department_key if user.department_key else "ALL"
        print(f"{user.email:<25} {user.role:<12} {dept}")
    
    print("\n" + "="*60)
    print("✅ SUCCESS! All departments and users created.")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
