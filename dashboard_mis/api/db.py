from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./dashboard.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    department_key = Column(String(20), primary_key=True, index=True)
    department_name = Column(String(100), nullable=False)
    cost_centre_parent = Column(String(100), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(20), nullable=False) # 'ADMIN', 'DEPT_HEAD'
    department_key = Column(String(20), ForeignKey("departments.department_key"), nullable=True)
    is_active = Column(Boolean, default=True)

    owner = relationship("Department")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
