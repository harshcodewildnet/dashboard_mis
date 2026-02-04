import sys
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from api.db import SessionLocal, init_db, User, Department

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_data(db: Session):
    # 1. Departments
    departments = [
        {"key": "DM", "name": "Digital Marketing", "cc_parent": "Digital Marketing"},
        {"key": "INT_DM", "name": "International DM", "cc_parent": "International D M"},
        {"key": "PPC", "name": "PPC", "cc_parent": "PPC"},
        {"key": "OH", "name": "Overhead", "cc_parent": "Overhead"},
        {"key": "SA", "name": "Staff Augmentation", "cc_parent": "Staff Augmentation"},
        {"key": "WE", "name": "Wildnet Edge", "cc_parent": "Wildnet Edge"},
    ]

    print("Seeding Departments...")
    for dept in departments:
        d = db.query(Department).filter(Department.department_key == dept["key"]).first()
        if not d:
            new_dept = Department(department_key=dept["key"], department_name=dept["name"], cost_centre_parent=dept["cc_parent"])
            db.add(new_dept)
    db.commit()

    # 2. Users
    users = [
        {"email": "admin@company.com", "pass": "admin123", "role": "ADMIN", "dept": None},
        {"email": "dm@company.com", "pass": "dm123", "role": "DEPT_HEAD", "dept": "DM"},
        {"email": "ppc@company.com", "pass": "ppc123", "role": "DEPT_HEAD", "dept": "PPC"},
        {"email": "intdm@company.com", "pass": "intdm123", "role": "DEPT_HEAD", "dept": "INT_DM"},
        {"email": "oh@company.com", "pass": "oh123", "role": "DEPT_HEAD", "dept": "OH"},
    ]

    print("Seeding Users...")
    for user in users:
        u = db.query(User).filter(User.email == user["email"]).first()
        if not u:
            hashed = get_password_hash(user["pass"])
            new_user = User(email=user["email"], password_hash=hashed, role=user["role"], department_key=user["dept"])
            db.add(new_user)
            print(f"Created: {user['email']}")
        else:
            print(f"Skipped (exists): {user['email']}")
    
    db.commit()

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    seed_data(db)
    print("Database Initialized and Seeded Successfully.")
