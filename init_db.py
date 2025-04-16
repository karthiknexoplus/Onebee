import random
from app import app, db
from models import User, Location, Lane, Device, VehicleUser, UserAccessPermission, AccessLog
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        
        # Create sample locations
        locations = [
            Location(name='Main Gate', address='123 Main Street', is_active=True),
            Location(name='Back Gate', address='456 Back Street', is_active=True),
            Location(name='Service Gate', address='789 Service Road', is_active=True)
        ]
        for location in locations:
            db.session.add(location)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create sample lanes for each location
        for location in locations:
            lanes = [
                Lane(
                    name=f'{location.name} Entry Lane',
                    lane_type='entry',
                    location=location,
                    is_active=True
                ),
                Lane(
                    name=f'{location.name} Exit Lane',
                    lane_type='exit',
                    location=location,
                    is_active=True
                )
            ]
            for lane in lanes:
                db.session.add(lane)
        
        # Commit to get lane IDs
        db.session.commit()
        
        # Create sample devices for each lane
        lanes = Lane.query.all()
        for lane in lanes:
            devices = [
                Device(
                    name=f'{lane.name} ANPR Camera',
                    device_type='anpr',
                    ip_address=f'192.168.1.{random.randint(100, 255)}',
                    port=random.randint(1000, 9999),
                    status='active',
                    lane_id=lane.id
                ),
                Device(
                    name=f'{lane.name} Fastag Reader',
                    device_type='fastag',
                    ip_address=f'192.168.1.{random.randint(100, 255)}',
                    port=random.randint(1000, 9999),
                    status='active',
                    lane_id=lane.id
                ),
                Device(
                    name=f'{lane.name} Gate Controller',
                    device_type='controller',
                    ip_address=f'192.168.1.{random.randint(100, 255)}',
                    port=random.randint(1000, 9999),
                    status='active',
                    lane_id=lane.id
                )
            ]
            for device in devices:
                db.session.add(device)
        
        # Final commit
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 