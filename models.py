from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle_users = db.relationship('VehicleUser', back_populates='location')
    lanes = db.relationship('Lane', back_populates='location')
    
    def __repr__(self):
        return f'<Location {self.name}>'

class VehicleUser(db.Model):
    __tablename__ = 'vehicle_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    vehicle_number = db.Column(db.String(20), unique=True, nullable=False)
    fastag_id = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    kyc_document_type = db.Column(db.String(50))
    kyc_document_number = db.Column(db.String(50))
    kyc_document_path = db.Column(db.String(200))
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')
    is_active = db.Column(db.Boolean, default=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = db.relationship('Location', back_populates='vehicle_users')
    access_permissions = db.relationship('UserAccessPermission', back_populates='vehicle_user', cascade='all, delete-orphan')
    access_logs = db.relationship('AccessLog', back_populates='vehicle_user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<VehicleUser {self.name}>'

class UserAccessPermission(db.Model):
    __tablename__ = 'user_access_permission'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('vehicle_users.id'), nullable=False)
    lane_id = db.Column(db.Integer, db.ForeignKey('lanes.id'), nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    days_of_week = db.Column(db.String(50))  # Comma-separated list of days
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle_user = db.relationship('VehicleUser', back_populates='access_permissions')
    lane = db.relationship('Lane', back_populates='access_permissions')

    def __repr__(self):
        return f'<UserAccessPermission {self.id}>'

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # 'fastag', 'controller', 'anpr'
    ip_address = db.Column(db.String(50), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'error'
    last_heartbeat = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key for lane relationship
    lane_id = db.Column(db.Integer, db.ForeignKey('lanes.id'))
    
    # Relationships
    lane = db.relationship('Lane', back_populates='devices')
    access_logs = db.relationship('AccessLog', back_populates='device', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Device {self.device_type} for Lane {self.lane_id}>'

class Lane(db.Model):
    __tablename__ = 'lanes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lane_type = db.Column(db.String(50), nullable=False)  # 'entry', 'exit'
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'maintenance'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key for location relationship
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    
    # Relationships
    location = db.relationship('Location', back_populates='lanes')
    devices = db.relationship('Device', back_populates='lane', cascade='all, delete-orphan')
    access_permissions = db.relationship('UserAccessPermission', back_populates='lane', cascade='all, delete-orphan')
    access_logs = db.relationship('AccessLog', back_populates='lane', cascade='all, delete-orphan')
    
    @property
    def fastag_reader(self):
        return next((d for d in self.devices if d.device_type == 'fastag'), None)
    
    @property
    def controller(self):
        return next((d for d in self.devices if d.device_type == 'controller'), None)
    
    @property
    def anpr_camera(self):
        return next((d for d in self.devices if d.device_type == 'anpr'), None)
    
    def __repr__(self):
        return f'<Lane {self.name}>'

class AccessLog(db.Model):
    __tablename__ = 'access_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('vehicle_users.id'), nullable=True)
    lane_id = db.Column(db.Integer, db.ForeignKey('lanes.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    access_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # granted or denied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle_user = db.relationship('VehicleUser', back_populates='access_logs')
    lane = db.relationship('Lane', back_populates='access_logs')
    device = db.relationship('Device', back_populates='access_logs')

    def __repr__(self):
        return f'<AccessLog {self.id}>'

class PresenceLog(db.Model):
    __tablename__ = 'presence_logs'
    id = db.Column(db.Integer, primary_key=True)
    lane_id = db.Column(db.Integer, db.ForeignKey('lanes.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    confidence = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'active' or 'inactive'
    
    # Relationships
    lane = db.relationship('Lane', backref=db.backref('presence_logs', lazy=True))
    device = db.relationship('Device', backref=db.backref('presence_logs', lazy=True))

    def __repr__(self):
        return f'<PresenceLog {self.id}>'

class BarrierLog(db.Model):
    __tablename__ = 'barrier_logs'
    id = db.Column(db.Integer, primary_key=True)
    lane_id = db.Column(db.Integer, db.ForeignKey('lanes.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    action = db.Column(db.String(20), nullable=False)  # 'open' or 'close'
    status = db.Column(db.String(20), nullable=False)  # 'success' or 'failed'
    error_message = db.Column(db.String(200))
    
    # Relationships
    lane = db.relationship('Lane', backref=db.backref('barrier_logs', lazy=True))
    device = db.relationship('Device', backref=db.backref('barrier_logs', lazy=True))

    def __repr__(self):
        return f'<BarrierLog {self.id}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action}>' 