from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
from models import db, Lane, Device, AccessLog, VehicleUser, UserAccessPermission, PresenceLog, BarrierLog, Location
from datetime import datetime
import json
from functools import wraps
from flask_login import current_user

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Initialize Flask-RESTX API
api = Api(api_bp,
    version='1.0',
    title='Access Control API',
    description='API for managing access control system',
    doc='/docs'
)

# Disable CSRF for API routes
@api_bp.before_request
def disable_csrf():
    pass

# Create namespaces
vehicle_ns = api.namespace('vehicle', description='Vehicle detection and ANPR operations')
barrier_ns = api.namespace('barrier', description='Barrier control operations')
health_ns = api.namespace('health', description='Hardware health check operations')
location_ns = api.namespace('locations', description='Location management operations')
lane_ns = api.namespace('lanes', description='Lane management operations')
user_ns = api.namespace('users', description='User management operations')

# Define models for Swagger documentation
vehicle_presence_model = api.model('VehiclePresence', {
    'lane_id': fields.Integer(required=True, description='ID of the lane'),
    'device_id': fields.Integer(required=True, description='ID of the sensor device'),
    'timestamp': fields.DateTime(required=True, description='Detection timestamp'),
    'confidence': fields.Float(required=True, description='Detection confidence score')
})

anpr_result_model = api.model('ANPRResult', {
    'lane_id': fields.Integer(required=True, description='ID of the lane'),
    'device_id': fields.Integer(required=True, description='ID of the ANPR camera'),
    'vehicle_number': fields.String(required=True, description='Detected vehicle number'),
    'confidence': fields.Float(required=True, description='Recognition confidence score'),
    'timestamp': fields.DateTime(required=True, description='Detection timestamp'),
    'image_path': fields.String(description='Path to captured image')
})

barrier_control_model = api.model('BarrierControl', {
    'lane_id': fields.Integer(required=True, description='ID of the lane'),
    'device_id': fields.Integer(required=True, description='ID of the barrier controller'),
    'action': fields.String(required=True, description='Action to perform (open/close)'),
    'timestamp': fields.DateTime(required=True, description='Command timestamp')
})

location_model = api.model('Location', {
    'id': fields.Integer(description='Location ID'),
    'name': fields.String(required=True, description='Location name'),
    'address': fields.String(description='Location address'),
    'is_active': fields.Boolean(description='Location status')
})

lane_model = api.model('Lane', {
    'id': fields.Integer(description='Lane ID'),
    'name': fields.String(required=True, description='Lane name'),
    'lane_type': fields.String(required=True, description='Lane type (entry/exit)'),
    'status': fields.String(description='Lane status'),
    'location_id': fields.Integer(required=True, description='Associated location ID')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'name': fields.String(required=True, description='User name'),
    'vehicle_number': fields.String(required=True, description='Vehicle number'),
    'fastag_id': fields.String(description='Fastag ID'),
    'location_id': fields.Integer(required=True, description='Associated location ID'),
    'is_active': fields.Boolean(description='User status')
})

health_check_model = api.model('HealthCheck', {
    'lane_id': fields.Integer(required=True, description='ID of the lane'),
    'device_id': fields.Integer(required=True, description='ID of the device'),
    'device_type': fields.String(required=True, description='Type of device'),
    'status': fields.String(required=True, description='Device status'),
    'last_heartbeat': fields.DateTime(required=True, description='Last heartbeat timestamp'),
    'error_message': fields.String(description='Error message if any')
})

reset_model = api.model('Reset', {
    'lane_id': fields.Integer(required=True, description='ID of the lane'),
    'device_id': fields.Integer(required=True, description='ID of the device'),
    'timestamp': fields.DateTime(required=True, description='Reset timestamp')
})

success_model = api.model('Success', {
    'status': fields.String(required=True, description='Status of the operation'),
    'message': fields.String(required=True, description='Message describing the result'),
    'data': fields.Raw(description='Response data')
})

def no_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Vehicle detection endpoints
@vehicle_ns.route('/presence')
class VehiclePresence(Resource):
    @vehicle_ns.expect(vehicle_presence_model)
    @vehicle_ns.doc(responses={
        200: 'Vehicle presence recorded successfully',
        400: 'Invalid input',
        404: 'Lane or device not found'
    })
    @vehicle_ns.doc(description='Record vehicle presence', 
                   example={
                       'lane_id': 1,
                       'device_id': 1,
                       'timestamp': '2024-04-08T10:00:00',
                       'confidence': 0.95
                   })
    def post(self):
        """Record vehicle presence"""
        try:
            data = request.json
            lane = Lane.query.get(data['lane_id'])
            device = Device.query.get(data['device_id'])
            
            if not lane or not device:
                return {'message': 'Lane or device not found'}, 404
            
            # Create presence log
            log = PresenceLog(
                lane_id=lane.id,
                device_id=device.id,
                timestamp=datetime.fromisoformat(data['timestamp']),
                confidence=data['confidence'],
                status='active' if data['confidence'] > 0.8 else 'inactive'
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'message': 'Vehicle presence recorded successfully',
                'status': log.status
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@vehicle_ns.route('/presence/reset')
class VehiclePresenceReset(Resource):
    @vehicle_ns.expect(reset_model)
    @vehicle_ns.doc(responses={
        200: 'Vehicle presence logs reset successfully',
        400: 'Invalid input',
        404: 'Lane or device not found'
    })
    @vehicle_ns.doc(description='Reset vehicle presence logs for a specific lane and device',
                   example={
                       'lane_id': 1,
                       'device_id': 1,
                       'timestamp': '2024-04-08T10:00:00'
                   })
    def post(self):
        """Reset vehicle presence logs"""
        try:
            data = request.json
            lane = Lane.query.get(data['lane_id'])
            device = Device.query.get(data['device_id'])
            
            if not lane or not device:
                return {'message': 'Lane or device not found'}, 404
            
            # Delete all presence logs for this lane and device
            PresenceLog.query.filter_by(
                lane_id=lane.id,
                device_id=device.id
            ).delete()
            
            db.session.commit()
            
            return {
                'message': 'Vehicle presence logs reset successfully',
                'lane_id': lane.id,
                'device_id': device.id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@vehicle_ns.route('/anpr')
class ANPRResult(Resource):
    @vehicle_ns.expect(anpr_result_model)
    @vehicle_ns.doc(responses={
        200: 'ANPR result processed successfully',
        400: 'Invalid input',
        404: 'Lane or device not found'
    })
    @vehicle_ns.doc(description='Process ANPR camera result',
                   example={
                       'lane_id': 1,
                       'device_id': 2,
                       'vehicle_number': 'KA 01 AB 1234',
                       'confidence': 0.98,
                       'timestamp': '2024-04-08T10:00:01',
                       'image_path': '/uploads/anpr/2024/04/08/image_001.jpg'
                   })
    def post(self):
        """Process ANPR camera result"""
        try:
            data = request.json
            lane = Lane.query.get(data['lane_id'])
            device = Device.query.get(data['device_id'])
            
            if not lane or not device:
                return {'message': 'Lane or device not found'}, 404
                
            # Find vehicle user
            vehicle_user = VehicleUser.query.filter_by(
                vehicle_number=data['vehicle_number']
            ).first()
            
            # Check access permission
            has_permission = False
            if vehicle_user and vehicle_user.is_active:
                permission = UserAccessPermission.query.filter_by(
                    user_id=vehicle_user.id,
                    lane_id=lane.id
                ).first()
                
                if permission:
                    # Check if current time is within allowed time range
                    current_time = datetime.fromisoformat(data['timestamp']).time()
                    if permission.start_time and permission.end_time:
                        if permission.start_time <= current_time <= permission.end_time:
                            # Check if current day is in allowed days
                            current_day = str(datetime.fromisoformat(data['timestamp']).weekday() + 1)
                            allowed_days = permission.days_of_week.split(',')
                            if current_day in allowed_days:
                                has_permission = True
                    else:
                        has_permission = True
            
            # Log the access attempt
            log = AccessLog(
                user_id=vehicle_user.id if vehicle_user else None,
                lane_id=lane.id,
                device_id=device.id,
                access_time=datetime.fromisoformat(data['timestamp']),
                status='granted' if has_permission else 'denied'
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'message': 'ANPR result processed successfully',
                'access_granted': has_permission,
                'vehicle_found': bool(vehicle_user)
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

# Barrier control endpoints
@barrier_ns.route('/control')
class BarrierControl(Resource):
    @barrier_ns.expect(barrier_control_model)
    @barrier_ns.doc(responses={
        200: 'Barrier control command sent successfully',
        400: 'Invalid input',
        404: 'Lane or device not found'
    })
    @barrier_ns.doc(description='Control barrier operation',
                   example={
                       'lane_id': 1,
                       'device_id': 3,
                       'action': 'open',
                       'timestamp': '2024-04-08T10:00:02'
                   })
    def post(self):
        """Control barrier (open/close)"""
        data = request.json
        
        # Validate lane exists
        lane = Lane.query.get(data['lane_id'])
        if not lane:
            return {'error': 'Lane not found'}, 404
            
        # Validate device exists and is a controller
        device = Device.query.filter_by(
            id=data['device_id'],
            device_type='controller'
        ).first()
        if not device:
            return {'error': 'Controller device not found'}, 404
            
        try:
            # Log the barrier action
            barrier_log = BarrierLog(
                lane_id=data['lane_id'],
                device_id=data['device_id'],
                action=data['action'],
                status='success'
            )
            db.session.add(barrier_log)
            db.session.commit()
            
            return {
                'message': f'Barrier {data["action"]}ed successfully',
                'timestamp': data['timestamp']
            }
        except Exception as e:
            # Log the failed action
            barrier_log = BarrierLog(
                lane_id=data['lane_id'],
                device_id=data['device_id'],
                action=data['action'],
                status='failed',
                error_message=str(e)
            )
            db.session.add(barrier_log)
            db.session.commit()
            
            return {'error': str(e)}, 500

# Health check endpoints
@health_ns.route('/check')
class HealthCheck(Resource):
    @health_ns.expect(health_check_model)
    @health_ns.doc(responses={
        200: 'Health check received successfully',
        400: 'Invalid input',
        404: 'Lane or device not found'
    })
    @health_ns.doc(description='Update device health status',
                  example={
                      'lane_id': 1,
                      'device_id': 1,
                      'device_type': 'sensor',
                      'status': 'active',
                      'last_heartbeat': '2024-04-08T10:00:00',
                      'error_message': None
                  })
    def post(self):
        """Update device health status"""
        try:
            data = request.json
            lane = Lane.query.get(data['lane_id'])
            device = Device.query.get(data['device_id'])
            
            if not lane or not device:
                return {'message': 'Lane or device not found'}, 404
                
            # Update device status
            device.status = data['status']
            device.last_heartbeat = datetime.fromisoformat(data['last_heartbeat'])
            db.session.commit()
            
            return {'message': 'Health check received successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@health_ns.route('/status/<int:lane_id>')
class LaneHealthStatus(Resource):
    @health_ns.doc(responses={
        200: 'Health status retrieved successfully',
        404: 'Lane not found'
    })
    @health_ns.doc(description='Get health status of all devices in a lane',
                  example={
                      'lane_id': 1,
                      'lane_name': 'Main Gate Lane 1',
                      'devices': [
                          {
                              'device_id': 1,
                              'device_type': 'sensor',
                              'status': 'active',
                              'last_heartbeat': '2024-04-08T10:00:00'
                          },
                          {
                              'device_id': 2,
                              'device_type': 'anpr',
                              'status': 'active',
                              'last_heartbeat': '2024-04-08T10:00:00'
                          }
                      ]
                  })
    def get(self, lane_id):
        """Get health status of all devices in a lane"""
        try:
            lane = Lane.query.get(lane_id)
            if not lane:
                return {'message': 'Lane not found'}, 404
                
            devices = Device.query.filter_by(lane_id=lane_id).all()
            status = {
                'lane_id': lane_id,
                'lane_name': lane.name,
                'devices': [{
                    'device_id': device.id,
                    'device_type': device.device_type,
                    'status': device.status,
                    'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None
                } for device in devices]
            }
            
            return status, 200
        except Exception as e:
            return {'message': str(e)}, 400

@health_ns.route('/reset')
class ResetDevice(Resource):
    @health_ns.expect(reset_model)
    @health_ns.doc(responses={
        200: 'Device reset successfully',
        400: 'Invalid input',
        404: 'Lane or device not found'
    })
    @health_ns.doc(description='Reset a device',
                  example={
                      'lane_id': 1,
                      'device_id': 1,
                      'timestamp': '2024-04-08T10:00:00'
                  })
    def post(self):
        """Reset a device"""
        try:
            data = request.json
            lane = Lane.query.get(data['lane_id'])
            device = Device.query.get(data['device_id'])
            
            if not lane or not device:
                return {'message': 'Lane or device not found'}, 404
            
            # Reset device status
            device.status = 'active'
            device.last_heartbeat = datetime.fromisoformat(data['timestamp'])
            device.error_message = None
            
            db.session.commit()
            
            return {
                'message': 'Device reset successfully',
                'device_status': device.status
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@api.route('/lane-device-counts')
class LaneDeviceCounts(Resource):
    @no_auth_required
    @api.doc('get_lane_device_counts')
    @api.marshal_with(success_model)
    def get(self):
        """Get counts of lanes and their associated devices"""
        try:
            # Get all lanes
            lanes = Lane.query.all()
            
            # Prepare response data
            response_data = {
                'total_lanes': len(lanes),
                'lanes': []
            }
            
            # For each lane, get its devices
            for lane in lanes:
                devices = Device.query.filter_by(lane_id=lane.id).all()
                lane_data = {
                    'lane_id': lane.id,
                    'lane_name': lane.name,
                    'total_devices': len(devices),
                    'devices': [
                        {
                            'device_id': device.id,
                            'device_name': device.name,
                            'device_type': device.device_type,
                            'status': device.status
                        }
                        for device in devices
                    ]
                }
                response_data['lanes'].append(lane_data)
            
            return {
                'status': 'success',
                'message': 'Lane and device counts retrieved successfully',
                'data': response_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error retrieving lane and device counts: {str(e)}'
            }, 500

@api.route('/users')
class UserManagement(Resource):
    @no_auth_required
    @api.expect(user_model)
    @api.doc('create_user')
    def post(self):
        """Create a new user"""
        try:
            data = request.json
            
            # Check if user with same fastag_id already exists
            existing_user = VehicleUser.query.filter_by(fastag_id=data['fastag_id']).first()
            if existing_user:
                return {
                    'status': 'error',
                    'message': 'User with this Fastag ID already exists',
                    'data': {
                        'user_id': existing_user.id,
                        'name': existing_user.name,
                        'vehicle_number': existing_user.vehicle_number
                    }
                }, 409  # 409 Conflict
            
            # Create new user
            user = VehicleUser(
                name=data['name'],
                designation=data['designation'],
                vehicle_number=data['vehicle_number'],
                fastag_id=data['fastag_id'],
                location_id=data['location_id'],
                kyc_document_type=data['kyc_document_type'],
                kyc_document_number=data['kyc_document_number'],
                valid_from=datetime.strptime(data['valid_from'], '%Y-%m-%d').date(),
                valid_to=datetime.strptime(data['valid_to'], '%Y-%m-%d').date(),
                is_active=data['is_active']
            )
            
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Add access permissions
            for permission in data['access_permissions']:
                access_permission = UserAccessPermission(
                    user_id=user.id,
                    lane_id=permission['lane_id'],
                    start_time=datetime.strptime(permission['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(permission['end_time'], '%H:%M').time(),
                    days_of_week=permission['days_of_week']
                )
                db.session.add(access_permission)
            
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'User created successfully',
                'data': {
                    'user_id': user.id,
                    'name': user.name,
                    'vehicle_number': user.vehicle_number
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'Error creating user: {str(e)}'
            }, 500 

@api.route('/users/<int:user_id>')
class UserManagementById(Resource):
    @no_auth_required
    @api.expect(api.model('UserUpdate', {
        'name': fields.String(description='Full name of the user'),
        'designation': fields.String(description='User designation'),
        'vehicle_number': fields.String(description='Vehicle registration number'),
        'location_id': fields.Integer(description='Location ID'),
        'is_active': fields.Boolean(description='User status')
    }))
    @api.doc('update_user')
    def put(self, user_id):
        """Update an existing user"""
        try:
            data = request.json
            user = VehicleUser.query.get(user_id)
            
            if not user:
                return {
                    'status': 'error',
                    'message': 'User not found'
                }, 404
            
            # Update user details
            if 'name' in data:
                user.name = data['name']
            if 'designation' in data:
                user.designation = data['designation']
            if 'vehicle_number' in data:
                user.vehicle_number = data['vehicle_number']
            if 'location_id' in data:
                user.location_id = data['location_id']
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'User updated successfully',
                'data': {
                    'user_id': user.id,
                    'name': user.name,
                    'vehicle_number': user.vehicle_number,
                    'is_active': user.is_active
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'Error updating user: {str(e)}'
            }, 500 

@location_ns.route('')
class LocationList(Resource):
    @location_ns.doc('list_locations')
    @location_ns.marshal_list_with(location_model)
    def get(self):
        """List all locations"""
        try:
            locations = Location.query.all()
            return locations
        except Exception as e:
            return {'message': str(e)}, 500

@location_ns.route('/<int:location_id>')
@location_ns.param('location_id', 'The location identifier')
class LocationDetail(Resource):
    @location_ns.doc('get_location')
    @location_ns.marshal_with(location_model)
    def get(self, location_id):
        """Get a specific location"""
        try:
            location = Location.query.get_or_404(location_id)
            return location
        except Exception as e:
            return {'message': str(e)}, 500

@lane_ns.route('')
class LaneList(Resource):
    @lane_ns.doc('list_lanes')
    @lane_ns.marshal_list_with(lane_model)
    def get(self):
        """List all lanes"""
        try:
            lanes = Lane.query.all()
            return lanes
        except Exception as e:
            return {'message': str(e)}, 500

@lane_ns.route('/<int:lane_id>')
@lane_ns.param('lane_id', 'The lane identifier')
class LaneDetail(Resource):
    @lane_ns.doc('get_lane')
    @lane_ns.marshal_with(lane_model)
    def get(self, lane_id):
        """Get a specific lane"""
        try:
            lane = Lane.query.get_or_404(lane_id)
            return lane
        except Exception as e:
            return {'message': str(e)}, 500

@lane_ns.route('/<int:lane_id>/devices')
@lane_ns.param('lane_id', 'The lane identifier')
class LaneDevices(Resource):
    @lane_ns.doc('get_lane_devices')
    def get(self, lane_id):
        """Get devices for a specific lane"""
        try:
            lane = Lane.query.get_or_404(lane_id)
            devices = Device.query.filter_by(lane_id=lane_id).all()
            return {
                'lane_id': lane_id,
                'lane_name': lane.name,
                'devices': [{
                    'id': device.id,
                    'name': device.name,
                    'device_type': device.device_type,
                    'status': device.status
                } for device in devices]
            }
        except Exception as e:
            return {'message': str(e)}, 500

@user_ns.route('')
class UserList(Resource):
    @user_ns.doc('list_users')
    @user_ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        try:
            users = VehicleUser.query.all()
            return users
        except Exception as e:
            return {'message': str(e)}, 500

@user_ns.route('/<int:user_id>')
@user_ns.param('user_id', 'The user identifier')
class UserDetail(Resource):
    @user_ns.doc('get_user')
    @user_ns.marshal_with(user_model)
    def get(self, user_id):
        """Get a specific user"""
        try:
            user = VehicleUser.query.get_or_404(user_id)
            return user
        except Exception as e:
            return {'message': str(e)}, 500 