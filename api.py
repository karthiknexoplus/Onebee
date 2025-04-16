from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
from models import db, Lane, Device, AccessLog, VehicleUser, UserAccessPermission, PresenceLog, BarrierLog
from datetime import datetime
import json
from functools import wraps
from flask_login import current_user

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Disable CSRF for API routes
@api_bp.before_request
def disable_csrf():
    pass

api = Api(api_bp, 
    version='1.0', 
    title='Access Control API',
    description='API for vehicle access control system',
    doc='/docs',  # Change the documentation URL to /docs
    # Customize Swagger UI theme
    template='''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Access Control API Documentation</title>
        <link rel="icon" type="image/png" href="/static/images/logo.png">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
            }
            .swagger-ui .topbar {
                background-color: #343a40;
            }
            .swagger-ui .info .title {
                color: #343a40;
            }
            .swagger-ui .opblock.opblock-post {
                border-color: #28a745;
                background: rgba(40, 167, 69, 0.1);
            }
            .swagger-ui .opblock.opblock-get {
                border-color: #007bff;
                background: rgba(0, 123, 255, 0.1);
            }
            .swagger-ui .btn.execute {
                background-color: #28a745;
            }
            .swagger-ui .btn.authorize {
                background-color: #343a40;
            }
            .swagger-ui .opblock .opblock-summary-method {
                background: #343a40;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: "/api/swagger.json",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    docExpansion: "list",
                    defaultModelsExpandDepth: -1
                });
                window.ui = ui;
            };
        </script>
    </body>
    </html>
    '''
)

# Create namespaces
vehicle_ns = api.namespace('vehicle', description='Vehicle detection and ANPR operations')
barrier_ns = api.namespace('barrier', description='Barrier control operations')
health_ns = api.namespace('health', description='Hardware health check operations')

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

# Define user model for Swagger documentation
user_model = api.model('User', {
    'name': fields.String(required=True, description='Full name of the user'),
    'designation': fields.String(required=True, description='User designation'),
    'vehicle_number': fields.String(required=True, description='Vehicle registration number'),
    'fastag_id': fields.String(required=True, description='Fastag ID'),
    'location_id': fields.Integer(required=True, description='Location ID'),
    'kyc_document_type': fields.String(required=True, description='Type of KYC document'),
    'kyc_document_number': fields.String(required=True, description='KYC document number'),
    'valid_from': fields.Date(required=True, description='Validity start date'),
    'valid_to': fields.Date(required=True, description='Validity end date'),
    'is_active': fields.Boolean(required=True, description='User status'),
    'access_permissions': fields.List(fields.Nested(api.model('AccessPermission', {
        'lane_id': fields.Integer(required=True, description='Lane ID'),
        'start_time': fields.String(required=True, description='Access start time'),
        'end_time': fields.String(required=True, description='Access end time'),
        'days_of_week': fields.String(required=True, description='Days of week (1-7, comma-separated)')
    })))
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
            if vehicle_user:
                permission = UserAccessPermission.query.filter_by(
                    user_id=vehicle_user.id,
                    lane_id=lane.id,
                    is_active=True
                ).first()
                has_permission = bool(permission)
            
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