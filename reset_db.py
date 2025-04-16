from app import app, db
from models import *
from init_db import init_db
import os

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('uploads/kyc', exist_ok=True)

# Reset and initialize database
with app.app_context():
    db.drop_all()
    db.create_all()
    init_db()
    print("Database has been reset and initialized successfully!") 