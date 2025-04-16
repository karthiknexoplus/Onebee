from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
from models import db, Lane, Device, AccessLog, VehicleUser, UserAccessPermission, PresenceLog
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
        """Control barrier operation"""
        try:
            data = request.json
            lane = Lane.query.get(data['lane_id'])
            device = Device.query.get(data['device_id'])
            
            if not lane or not device:
                return {'message': 'Lane or device not found'}, 404
                
            if device.device_type != 'controller':
                return {'message': 'Invalid device type'}, 400
                
            # Here you would implement the actual barrier control logic
            # For now, we'll just log the command
            print(f"Barrier {data['action']} command sent to lane {lane.id}")
            
            return {'message': f"Barrier {data['action']} command sent successfully"}, 200
        except Exception as e:
            return {'message': str(e)}, 400

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