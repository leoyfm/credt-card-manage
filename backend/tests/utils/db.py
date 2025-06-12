from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
def create_test_session():
    engine = create_engine("postgresql://credit_user:credit_password@localhost:5432/test")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal() 