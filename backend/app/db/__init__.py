"""Database layer"""
from app.db.database import Base, engine, SessionLocal, get_db
from app.db import models

# Create all tables
def init_db():
    """Initialize database tables"""
    models.Base.metadata.create_all(bind=engine)
