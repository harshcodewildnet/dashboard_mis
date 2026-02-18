import sys
sys.path.insert(0, '/app')

from api.db import SessionLocal, User, Department
from api.auth import pwd_context

def main():
    db = SessionLocal()
    try:
        print("="*60)
        print("ADDING WILDNET RESTRICTED USER")
        print("="*60)
        
        # 1. Verify Department Exists
        dept_key = "WE"
        dept_name = "Wildnet Edge"
        
        dept = db.query(Department).filter(Department.department_key == dept_key).first()
        if not dept:
            print(f"Adding missing department: {dept_name}")
            new_dept = Department(
                department_key=dept_key,
                department_name=dept_name,
                cost_centre_parent=dept_name # Assuming cost centre name matches
            )
            db.add(new_dept)
            db.commit()
            print("✓ Department Created")
        else:
            print(f"✓ Department '{dept.department_name}' found.")

        # 2. Key User Data
        email = "wildnet@company.com"
        password = "wildnet123" # Simple default
        role = "DEPT_HEAD"
        
        # 3. Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            print(f"User {email} already exists. Updating department...")
            existing_user.department_key = dept_key
            existing_user.role = role
            # Update password if needed, but let's keep it safe
            # existing_user.password_hash = pwd_context.hash(password) 
            db.commit()
            print(f"✓ User updated to restricted department: {dept_key}")
        else:
            print(f"Creating new user: {email}")
            new_user = User(
                email=email,
                password_hash=pwd_context.hash(password),
                role=role,
                department_key=dept_key
            )
            db.add(new_user)
            db.commit()
            print(f"✓ User created successfully!")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
