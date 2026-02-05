import sys
import os
sys.path.append('/app')

from api.db import SessionLocal, User
from api.auth import verify_password, pwd_context

def test():
    db = SessionLocal()
    user = db.query(User).filter(User.email == 'admin@company.com').first()
    
    if not user:
        print("User not found in DB!")
        return

    print(f"User found: {user.email}")
    print(f"Stored Hash: {user.password_hash}")
    
    password_to_test = 'admin123'
    is_valid = verify_password(password_to_test, user.password_hash)
    print(f"Verify '{password_to_test}': {is_valid}")
    
    # Try hashing again and verifying
    new_hash = pwd_context.hash(password_to_test)
    print(f"New Hash: {new_hash}")
    print(f"Verify against new hash: {pwd_context.verify(password_to_test, new_hash)}")

if __name__ == "__main__":
    test()
