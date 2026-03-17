'''
only for user login.
SQLite connection + SQLAlchemy setup 
-> opens the connection to eg. data/notebook.db
'''


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import SQLITE_URL

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

# FastAPI dependency, yields a DB session and closes after request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()