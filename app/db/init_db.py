"""
Call this once on startup or in main.py to auto-create tables.
"""
from app.db.session import Base, engine
from app.db import models  # ensures all models are imported

# Create all tables if not exist
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
