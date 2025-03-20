from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = 'sqlite:///data.db'
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autoflush=False, autocommit=False , bind=engine)
Base = declarative_base()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()