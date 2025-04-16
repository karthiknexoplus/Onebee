from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Lane, Device, Location, VehicleUser, UserAccessPermission, AccessLog, PresenceLog
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import io
from flask_migrate import Migrate
from fpdf import FPDF
import csv
import random
import string
from api import api_bp  # Import the API blueprint

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///access_control.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Register API blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
with app.app_context():
    db.create_all()  # Create tables if they don't exist
    
    # Create admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
    
    # Create sample locations if not exists
    if not Location.query.first():
        locations = [
            Location(name='Main Gate', address='123 Main Street', is_active=True),
            Location(name='Back Gate', address='456 Back Street', is_active=True),
            Location(name='Service Gate', address='789 Service Road', is_active=True)
        ]
        for location in locations:
            db.session.add(location)
        db.session.commit()
    
    # Create sample lanes if not exists
    if not Lane.query.first():
        locations = Location.query.all()
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
        db.session.commit()

@app.route('/')
@login_required
def index():
    # Get counts for summary cards
    users = VehicleUser.query.all()
    active_users = len([u for u in users if u.is_active])
    
    lanes = Lane.query.all()
    active_lanes = len([l for l in lanes if l.status == 'active'])
    
    locations = Location.query.all()
    active_locations = len([l for l in locations if l.is_active])
    
    # Get today's access counts
    today = datetime.now().date()
    today_logs = AccessLog.query.filter(
        db.func.date(AccessLog.access_time) == today
    ).all()
    today_access = len(today_logs)
    today_denied = len([log for log in today_logs if log.status == 'denied'])
    
    # Get vehicle type counts
    two_wheeler_count = len([u for u in users if u.vehicle_number.startswith(('KA', 'MH', 'TN'))])
    four_wheeler_count = len([u for u in users if not u.vehicle_number.startswith(('KA', 'MH', 'TN'))])
    
    # Get time distribution
    time_distribution = [0] * 6  # 4-hour intervals
    for log in today_logs:
        hour = log.access_time.hour
        interval = hour // 4
        if interval < 6:
            time_distribution[interval] += 1
    
    # Get location data
    location_names = [loc.name for loc in locations]
    location_counts = []
    for location in locations:
        count = sum(len(lane.access_logs) for lane in location.lanes)
        location_counts.append(count)
    
    # Get day distribution
    day_distribution = [0] * 7
    for log in today_logs:
        day = log.access_time.weekday()
        day_distribution[day] += 1
    
    # Get recent logs
    recent_logs = AccessLog.query.order_by(AccessLog.access_time.desc()).limit(10).all()
    
    return render_template('dashboard.html',
                         users=users,
                         active_users=active_users,
                         lanes=lanes,
                         active_lanes=active_lanes,
                         locations=locations,
                         active_locations=active_locations,
                         today_access=today_access,
                         today_denied=today_denied,
                         two_wheeler_count=two_wheeler_count,
                         four_wheeler_count=four_wheeler_count,
                         time_distribution=time_distribution,
                         location_names=location_names,
                         location_counts=location_counts,
                         day_distribution=day_distribution,
                         recent_logs=recent_logs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('signup'))
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Settings routes
@app.route('/settings')
@login_required
def settings():
    lanes = Lane.query.all()
    return render_template('settings.html', lanes=lanes)

@app.route('/settings/lane/add', methods=['POST'])
@login_required
def add_lane():
    name = request.form.get('name')
    lane_type = request.form.get('lane_type')
    
    # Create new lane
    lane = Lane(
        name=name,
        lane_type=lane_type,
        status='active'
    )
    db.session.add(lane)
    db.session.commit()
    
    # Add devices if enabled
    if request.form.get('enable_fastag'):
        fastag = Device(
            name=f'{name} Fastag',
            device_type='fastag',
            ip_address=request.form.get('fastag_ip'),
            port=request.form.get('fastag_port'),
            status='active',
            lane_id=lane.id
        )
        db.session.add(fastag)
    
    if request.form.get('enable_controller'):
        controller = Device(
            name=f'{name} Controller',
            device_type='controller',
            ip_address=request.form.get('controller_ip'),
            port=request.form.get('controller_port'),
            status='active',
            lane_id=lane.id
        )
        db.session.add(controller)
    
    if request.form.get('enable_anpr'):
        anpr = Device(
            name=f'{name} ANPR',
            device_type='anpr',
            ip_address=request.form.get('anpr_ip'),
            port=request.form.get('anpr_port'),
            status='active',
            lane_id=lane.id
        )
        db.session.add(anpr)
    
    db.session.commit()
    flash('Lane added successfully')
    return redirect(url_for('settings'))

@app.route('/settings/lane/<int:lane_id>/edit', methods=['POST'])
@login_required
def edit_lane(lane_id):
    lane = db.session.get(Lane, lane_id)
    if not lane:
        abort(404)
    
    # Update lane details
    lane.name = request.form.get('name')
    lane.lane_type = request.form.get('lane_type')
    lane.status = request.form.get('status', 'active')
    
    # Update or create devices
    def update_device(device_type, enable_key, ip_key, port_key):
        device = next((d for d in lane.devices if d.device_type == device_type), None)
        is_enabled = bool(request.form.get(enable_key))
        
        if is_enabled:
            if not device:
                device = Device(
                    name=f'{lane.name} {device_type.title()}',
                    device_type=device_type,
                    lane_id=lane.id
                )
                db.session.add(device)
            device.ip_address = request.form.get(ip_key)
            device.port = request.form.get(port_key)
            device.status = 'active'
        elif device:
            device.status = 'inactive'
    
    update_device('fastag', 'enable_fastag', 'fastag_ip', 'fastag_port')
    update_device('controller', 'enable_controller', 'controller_ip', 'controller_port')
    update_device('anpr', 'enable_anpr', 'anpr_ip', 'anpr_port')
    
    db.session.commit()
    flash('Lane updated successfully')
    return redirect(url_for('settings'))

@app.route('/settings/lane/<int:lane_id>/delete', methods=['POST'])
@login_required
def delete_lane(lane_id):
    lane = db.session.get(Lane, lane_id)
    if not lane:
        abort(404)
    
    # Delete associated devices
    Device.query.filter_by(lane_id=lane.id).delete()
    
    # Delete lane
    db.session.delete(lane)
    db.session.commit()
    
    flash('Lane deleted successfully')
    return redirect(url_for('settings'))

@app.route('/api/lanes/<int:lane_id>')
@login_required
def get_lane(lane_id):
    lane = db.session.get(Lane, lane_id)
    if not lane:
        abort(404)
    return jsonify({
        'id': lane.id,
        'name': lane.name,
        'lane_type': lane.lane_type,
        'status': lane.status,
        'fastag_reader': {
            'id': lane.fastag_reader.id if lane.fastag_reader else None,
            'is_enabled': lane.fastag_reader.status == 'active' if lane.fastag_reader else False,
            'ip_address': lane.fastag_reader.ip_address if lane.fastag_reader else '',
            'port': lane.fastag_reader.port if lane.fastag_reader else ''
        } if lane.fastag_reader else None,
        'controller': {
            'id': lane.controller.id if lane.controller else None,
            'is_enabled': lane.controller.status == 'active' if lane.controller else False,
            'ip_address': lane.controller.ip_address if lane.controller else '',
            'port': lane.controller.port if lane.controller else ''
        } if lane.controller else None,
        'anpr_camera': {
            'id': lane.anpr_camera.id if lane.anpr_camera else None,
            'is_enabled': lane.anpr_camera.status == 'active' if lane.anpr_camera else False,
            'ip_address': lane.anpr_camera.ip_address if lane.anpr_camera else '',
            'port': lane.anpr_camera.port if lane.anpr_camera else ''
        } if lane.anpr_camera else None
    })

# User Management Routes
@app.route('/users')
@login_required
def users():
    users = VehicleUser.query.all()
    locations = Location.query.all()
    lanes = Lane.query.all()
    return render_template('users.html', users=users, locations=locations, lanes=lanes)

@app.route('/faq')
@login_required
def faq():
    return render_template('faq.html')

@app.route('/user-manual')
@login_required
def user_manual():
    return render_template('user_manual.html')

@app.route('/users/add', methods=['POST'])
@login_required
def add_user():
    # Create new user
    user = VehicleUser(
        name=request.form.get('name'),
        designation=request.form.get('designation'),
        vehicle_number=request.form.get('vehicle_number'),
        fastag_id=request.form.get('fastag_id'),
        location_id=request.form.get('location_id'),
        kyc_document_type=request.form.get('kyc_document_type'),
        kyc_document_number=request.form.get('kyc_document_number'),
        valid_from=datetime.strptime(request.form.get('valid_from'), '%Y-%m-%d').date(),
        valid_to=datetime.strptime(request.form.get('valid_to'), '%Y-%m-%d').date(),
        is_active=True
    )
    
    # Handle KYC document upload
    if 'kyc_document' in request.files:
        file = request.files['kyc_document']
        if file.filename:
            filename = f"kyc_{user.vehicle_number}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.kyc_document_path = filename
    
    db.session.add(user)
    db.session.commit()
    
    # Add access permissions
    lane_ids = request.form.getlist('access_lanes')
    days_of_week = request.form.getlist('days_of_week')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    for lane_id in lane_ids:
        permission = UserAccessPermission(
            user_id=user.id,
            lane_id=lane_id,
            start_time=datetime.strptime(start_time, '%H:%M').time() if start_time else None,
            end_time=datetime.strptime(end_time, '%H:%M').time() if end_time else None,
            days_of_week=','.join(days_of_week)
        )
        db.session.add(permission)
    
    db.session.commit()
    flash('User added successfully')
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
def edit_user(user_id):
    user = db.session.get(VehicleUser, user_id)
    if not user:
        abort(404)
    
    # Update user details
    user.name = request.form.get('name')
    user.designation = request.form.get('designation')
    user.vehicle_number = request.form.get('vehicle_number')
    user.fastag_id = request.form.get('fastag_id')
    user.location_id = request.form.get('location_id')
    user.kyc_document_type = request.form.get('kyc_document_type')
    user.kyc_document_number = request.form.get('kyc_document_number')
    user.valid_from = datetime.strptime(request.form.get('valid_from'), '%Y-%m-%d').date()
    user.valid_to = datetime.strptime(request.form.get('valid_to'), '%Y-%m-%d').date()
    user.is_active = bool(request.form.get('is_active'))
    
    # Handle KYC document upload
    if 'kyc_document' in request.files:
        file = request.files['kyc_document']
        if file.filename:
            filename = f"kyc_{user.vehicle_number}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.kyc_document_path = filename
    
    # Update access permissions
    UserAccessPermission.query.filter_by(user_id=user.id).delete()
    
    lane_ids = request.form.getlist('access_lanes')
    days_of_week = request.form.getlist('days_of_week')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    for lane_id in lane_ids:
        permission = UserAccessPermission(
            user_id=user.id,
            lane_id=lane_id,
            start_time=datetime.strptime(start_time, '%H:%M').time() if start_time else None,
            end_time=datetime.strptime(end_time, '%H:%M').time() if end_time else None,
            days_of_week=','.join(days_of_week)
        )
        db.session.add(permission)
    
    db.session.commit()
    flash('User updated successfully')
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = db.session.get(VehicleUser, user_id)
    if not user:
        abort(404)
    
    # Delete associated access permissions
    UserAccessPermission.query.filter_by(user_id=user.id).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully')
    return redirect(url_for('users'))

@app.route('/api/users/<int:user_id>')
@login_required
def get_user(user_id):
    user = db.session.get(VehicleUser, user_id)
    if not user:
        abort(404)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'designation': user.designation,
        'vehicle_number': user.vehicle_number,
        'fastag_id': user.fastag_id,
        'location_id': user.location_id,
        'kyc_document_type': user.kyc_document_type,
        'kyc_document_number': user.kyc_document_number,
        'valid_from': user.valid_from.strftime('%Y-%m-%d'),
        'valid_to': user.valid_to.strftime('%Y-%m-%d'),
        'is_active': user.is_active,
        'access_permissions': [{
            'lane_id': p.lane_id,
            'start_time': p.start_time.strftime('%H:%M') if p.start_time else None,
            'end_time': p.end_time.strftime('%H:%M') if p.end_time else None,
            'days_of_week': p.days_of_week
        } for p in user.access_permissions]
    })

# Location Management Routes
@app.route('/locations/add', methods=['POST'])
@login_required
def add_location():
    location = Location(
        name=request.form.get('name'),
        address=request.form.get('address')
    )
    db.session.add(location)
    db.session.commit()
    flash('Location added successfully')
    return redirect(url_for('users'))

@app.route('/locations/<int:location_id>/edit', methods=['POST'])
@login_required
def edit_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        abort(404)
    location.name = request.form.get('name')
    location.address = request.form.get('address')
    db.session.commit()
    flash('Location updated successfully')
    return redirect(url_for('users'))

@app.route('/locations/<int:location_id>/delete', methods=['POST'])
@login_required
def delete_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        abort(404)
    db.session.delete(location)
    db.session.commit()
    flash('Location deleted successfully')
    return redirect(url_for('users'))

@app.route('/api/locations/<int:location_id>')
@login_required
def get_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        abort(404)
    return jsonify({
        'id': location.id,
        'name': location.name,
        'address': location.address
    })

# Report routes
@app.route('/reports/<report_type>')
@login_required
def report(report_type):
    # Get filter parameters
    location_id = request.args.get('location')
    lane_id = request.args.get('lane')
    date_range = request.args.get('range', 'today')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get all locations and lanes for dropdowns
    locations = Location.query.all()
    lanes = Lane.query.all()

    # Get report data based on filters
    report_data = []
    if report_type == 'daily':
        report_data = get_daily_report()
    elif report_type == 'weekly':
        report_data = get_weekly_report()
    elif report_type == 'monthly':
        report_data = get_monthly_report()
    elif report_type == 'vehicle':
        report_data = get_vehicle_report()
    elif report_type == 'location':
        report_data = get_location_report()

    return render_template('reports.html', 
                         report_type=report_type,
                         report_data=report_data,
                         locations=locations,
                         lanes=lanes)

@app.route('/reports/export/<report_type>')
@login_required
def export_report(report_type):
    # Get filter parameters
    location_id = request.args.get('location')
    lane_id = request.args.get('lane')
    date_range = request.args.get('range', 'today')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format = request.args.get('format', 'csv')

    # Get report data based on filters
    report_data = []
    if report_type == 'daily':
        report_data = get_daily_report()
    elif report_type == 'weekly':
        report_data = get_weekly_report()
    elif report_type == 'monthly':
        report_data = get_monthly_report()
    elif report_type == 'vehicle':
        report_data = get_vehicle_report()
    elif report_type == 'location':
        report_data = get_location_report()

    # Export based on format
    if format == 'csv':
        return export_to_csv(report_data)
    elif format == 'pdf':
        return export_to_pdf(report_data)
    else:
        return "Unsupported format", 400

def export_to_csv(data):
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Date', 'Location', 'Lane', 'Vehicle Number', 'Fastag ID', 'Access Time', 'Status'])
    
    # Write data
    for row in data:
        writer.writerow([
            row['date'],
            row['location'],
            row['lane'],
            row['vehicle_number'],
            row['fastag_id'],
            row['access_time'],
            row['status']
        ])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=report.csv"}
    )

def export_to_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add headers
    headers = ['Date', 'Location', 'Lane', 'Vehicle Number', 'Fastag ID', 'Access Time', 'Status']
    for header in headers:
        pdf.cell(40, 10, header, 1)
    pdf.ln()
    
    # Add data
    for row in data:
        pdf.cell(40, 10, str(row['date']), 1)
        pdf.cell(40, 10, str(row['location']), 1)
        pdf.cell(40, 10, str(row['lane']), 1)
        pdf.cell(40, 10, str(row['vehicle_number']), 1)
        pdf.cell(40, 10, str(row['fastag_id']), 1)
        pdf.cell(40, 10, str(row['access_time']), 1)
        pdf.cell(40, 10, str(row['status']), 1)
        pdf.ln()
    
    return Response(
        pdf.output(dest='S').encode('latin-1'),
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=report.pdf'}
    )

# Report helper functions
def get_daily_report():
    today = datetime.now().date()
    logs = AccessLog.query.filter(
        db.func.date(AccessLog.access_time) == today
    ).all()
    
    data = {
        'total_access': len(logs),
        'granted_access': len([log for log in logs if log.status == 'granted']),
        'denied_access': len([log for log in logs if log.status == 'denied']),
        'by_hour': {},
        'by_lane': {},
        'by_device': {}
    }
    
    for log in logs:
        hour = log.access_time.hour
        data['by_hour'][hour] = data['by_hour'].get(hour, 0) + 1
        
        if log.lane:
            lane_name = log.lane.name
            data['by_lane'][lane_name] = data['by_lane'].get(lane_name, 0) + 1
        
        if log.device:
            device_name = f"{log.device.device_type} - {log.device.ip_address}"
            data['by_device'][device_name] = data['by_device'].get(device_name, 0) + 1
    
    return data

def get_weekly_report():
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    logs = AccessLog.query.filter(
        db.func.date(AccessLog.access_time) >= week_start,
        db.func.date(AccessLog.access_time) <= today
    ).all()
    
    data = {
        'total_access': len(logs),
        'granted_access': len([log for log in logs if log.status == 'granted']),
        'denied_access': len([log for log in logs if log.status == 'denied']),
        'by_day': {},
        'by_lane': {},
        'by_device': {}
    }
    
    for log in logs:
        day = log.access_time.date()
        data['by_day'][day.strftime('%Y-%m-%d')] = data['by_day'].get(day.strftime('%Y-%m-%d'), 0) + 1
        
        if log.lane:
            lane_name = log.lane.name
            data['by_lane'][lane_name] = data['by_lane'].get(lane_name, 0) + 1
        
        if log.device:
            device_name = f"{log.device.device_type} - {log.device.ip_address}"
            data['by_device'][device_name] = data['by_device'].get(device_name, 0) + 1
    
    return data

def get_monthly_report():
    today = datetime.now().date()
    month_start = today.replace(day=1)
    logs = AccessLog.query.filter(
        db.func.date(AccessLog.access_time) >= month_start,
        db.func.date(AccessLog.access_time) <= today
    ).all()
    
    data = {
        'total_access': len(logs),
        'granted_access': len([log for log in logs if log.status == 'granted']),
        'denied_access': len([log for log in logs if log.status == 'denied']),
        'by_day': {},
        'by_lane': {},
        'by_device': {}
    }
    
    for log in logs:
        day = log.access_time.date()
        data['by_day'][day.strftime('%Y-%m-%d')] = data['by_day'].get(day.strftime('%Y-%m-%d'), 0) + 1
        
        if log.lane:
            lane_name = log.lane.name
            data['by_lane'][lane_name] = data['by_lane'].get(lane_name, 0) + 1
        
        if log.device:
            device_name = f"{log.device.device_type} - {log.device.ip_address}"
            data['by_device'][device_name] = data['by_device'].get(device_name, 0) + 1
    
    return data

def get_vehicle_report():
    try:
        # Get all logs with their related data
        logs = AccessLog.query.all()
        
        # Initialize the data structure
        data = {
            'total_vehicles': VehicleUser.query.count(),
            'active_vehicles': VehicleUser.query.filter(VehicleUser.valid_to >= datetime.now()).count(),
            'expired_vehicles': VehicleUser.query.filter(VehicleUser.valid_to < datetime.now()).count(),
            'by_location': {},
            'access_frequency': {},
            'status_distribution': {'granted': 0, 'denied': 0}
        }
        
        # Process each log
        for log in logs:
            # Count status distribution
            if log.status in ['granted', 'denied']:
                data['status_distribution'][log.status] = data['status_distribution'].get(log.status, 0) + 1
            
            # Process user-related data if user exists
            if log.vehicle_user:
                # Handle location
                location_name = 'Unknown'
                if log.vehicle_user.location:
                    location_name = log.vehicle_user.location.name
                data['by_location'][location_name] = data['by_location'].get(location_name, 0) + 1
                
                # Handle vehicle number
                vehicle_id = log.vehicle_user.vehicle_number
                if vehicle_id:
                    data['access_frequency'][vehicle_id] = data['access_frequency'].get(vehicle_id, 0) + 1
        
        return data
    except Exception as e:
        print(f"Error in get_vehicle_report: {str(e)}")
        # Return a safe default structure if there's an error
        return {
            'total_vehicles': 0,
            'active_vehicles': 0,
            'expired_vehicles': 0,
            'by_location': {},
            'access_frequency': {},
            'status_distribution': {'granted': 0, 'denied': 0}
        }

def get_location_report():
    locations = Location.query.all()
    data = {
        'total_locations': len(locations),
        'active_locations': len([loc for loc in locations if loc.is_active]),
        'inactive_locations': len([loc for loc in locations if not loc.is_active]),
        'by_location': {},
        'device_distribution': {},
        'access_patterns': {}
    }
    
    for location in locations:
        location_data = {
            'name': location.name,
            'address': location.address,
            'lanes': len(location.lanes),
            'devices': sum(len(lane.devices) for lane in location.lanes),
            'access_count': 0,
            'granted_count': 0,
            'denied_count': 0
        }
        
        for lane in location.lanes:
            for log in lane.access_logs:
                location_data['access_count'] += 1
                if log.status == 'granted':
                    location_data['granted_count'] += 1
                else:
                    location_data['denied_count'] += 1
                
                for device in lane.devices:
                    device_name = f"{device.device_type} - {device.ip_address}"
                    data['device_distribution'][device_name] = data['device_distribution'].get(device_name, 0) + 1
        
        data['by_location'][location.name] = location_data
    
    return data

def generate_random_string(length=8):
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_vehicle_number():
    """Generate a random vehicle number"""
    states = ['KA', 'MH', 'TN', 'AP', 'KL', 'DL', 'UP', 'GJ']
    return f"{random.choice(states)} {random.randint(10, 99)} {random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)} {random.randint(1000, 9999)}"

@app.route('/generate_test_data/<data_type>', methods=['POST'])
@login_required
def generate_test_data(data_type):
    try:
        # Get count from either form data or JSON
        if request.is_json:
            data = request.get_json()
            count = int(data.get('count', 5))
        else:
            count = int(request.form.get('count', 5))
            
        if count < 1 or count > 10:
            return jsonify({'error': 'Count must be between 1 and 10'}), 400

        if data_type == 'locations':
            # Generate test locations
            locations = []
            for i in range(count):
                location = Location(
                    name=f'Test Location {i+1}',
                    address=f'Test Address {i+1}',
                    city='Test City',
                    state='Test State',
                    country='Test Country',
                    postal_code='12345',
                    created_at=datetime.utcnow()
                )
                db.session.add(location)
                locations.append({
                    'id': location.id,
                    'name': location.name,
                    'address': location.address
                })
            db.session.commit()
            return jsonify({'message': f'Generated {count} test locations', 'data': locations})

        elif data_type == 'lanes':
            # Generate test lanes
            location = Location.query.first()
            if not location:
                return jsonify({'error': 'No locations found. Please generate locations first.'}), 400

            lanes = []
            for i in range(count):
                lane = Lane(
                    location_id=location.id,
                    name=f'Test Lane {i+1}',
                    lane_type='entry',
                    status='active',
                    created_at=datetime.utcnow()
                )
                db.session.add(lane)
                lanes.append({
                    'id': lane.id,
                    'name': lane.name,
                    'location_id': lane.location_id
                })
            db.session.commit()
            return jsonify({'message': f'Generated {count} test lanes', 'data': lanes})

        elif data_type == 'devices':
            # Generate test devices
            lane = Lane.query.first()
            if not lane:
                return jsonify({'error': 'No lanes found. Please generate lanes first.'}), 400

            devices = []
            for i in range(count):
                device = Device(
                    lane_id=lane.id,
                    name=f'Test Device {i+1}',
                    device_type='sensor',
                    status='active',
                    created_at=datetime.utcnow()
                )
                db.session.add(device)
                devices.append({
                    'id': device.id,
                    'name': device.name,
                    'lane_id': device.lane_id
                })
            db.session.commit()
            return jsonify({'message': f'Generated {count} test devices', 'data': devices})

        else:
            return jsonify({'error': 'Invalid data type'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/clear_test_data', methods=['POST'])
@login_required
def clear_test_data():
    try:
        # Delete all data from all tables
        AccessLog.query.delete()
        Device.query.delete()
        Lane.query.delete()
        Location.query.delete()
        VehicleUser.query.delete()
        UserAccessPermission.query.delete()
        
        db.session.commit()
        flash('All data has been cleared', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing data: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/reset_database', methods=['POST'])
@login_required
def reset_database():
    try:
        # Close any existing connections
        db.session.close()
        
        # Delete the database file
        db_path = 'access_control.db'
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user if it doesn't exist
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
        
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
        
        flash('Database has been reset to initial state', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting database: {str(e)}', 'error')
    finally:
        db.session.close()
    
    return redirect(url_for('index'))

@app.route('/vehicle-presence')
@login_required
def vehicle_presence():
    return render_template('vehicle_presence.html')

@app.route('/api/vehicle/presence/logs')
@login_required
def get_presence_logs():
    # Get the last 50 presence logs
    logs = PresenceLog.query.order_by(PresenceLog.timestamp.desc()).limit(50).all()
    
    return jsonify([{
        'timestamp': log.timestamp.isoformat(),
        'lane_name': log.lane.name if log.lane else 'Unknown',
        'device_name': log.device.name if log.device else 'Unknown',
        'confidence': log.confidence,
        'status': log.status
    } for log in logs])

@app.route('/debug/db')
@login_required
def debug_db():
    lanes = Lane.query.all()
    devices = Device.query.all()
    return jsonify({
        'lanes': [{'id': lane.id, 'name': lane.name} for lane in lanes],
        'devices': [{'id': device.id, 'name': device.name, 'lane_id': device.lane_id} for device in devices]
    })

@app.route('/api-test')
@login_required
def api_test():
    return render_template('api_test.html')

# Error handlers
@app.errorhandler(400)
def bad_request_error(error):
    if request.is_json:
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400
    flash('Bad Request: ' + str(error))
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    if request.is_json:
        return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found'}), 404
    flash('Resource not found')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.is_json:
        return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500
    flash('An unexpected error occurred')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000) 