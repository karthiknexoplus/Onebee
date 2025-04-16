from fpdf import FPDF
from datetime import datetime

class APIDocumentation(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Onebee Access Control System API Documentation', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        # Copyright
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, '© 2024 Onebee Technology. All rights reserved.', 0, 0, 'C')

def generate_api_docs():
    pdf = APIDocumentation()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title Page
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 60, 'Onebee Access Control System', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'API Documentation', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Version 1.0', 0, 1, 'C')
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 10, 'This document contains proprietary information of Onebee Technology. Unauthorized reproduction or distribution of this document, or any portion of it, may result in severe civil and criminal penalties.')
    
    # Table of Contents
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Table of Contents', 0, 1, 'L')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    contents = [
        '1. Introduction',
        '2. Interactive API Documentation (Swagger UI)',
        '3. Authentication',
        '4. Base URL',
        '5. API Endpoints',
        '   5.1 User Management',
        '   5.2 Location Management',
        '   5.3 Lane Management',
        '   5.4 Device Management',
        '   5.5 Access Logs',
        '   5.6 Vehicle Management',
        '   5.7 Barrier Management',
        '   5.8 Health Management',
        '6. Response Codes',
        '7. Error Handling',
        '8. Rate Limiting',
        '9. Examples',
        '10. Using Swagger UI'
    ]
    for item in contents:
        pdf.cell(0, 10, item, 0, 1, 'L')
    
    # Introduction
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '1. Introduction', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'The Onebee Access Control System API provides a comprehensive set of endpoints for managing access control operations. This API allows you to manage users, locations, lanes, devices, and access logs programmatically.')
    
    # Interactive API Documentation (Swagger UI)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '2. Interactive API Documentation (Swagger UI)', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'The Onebee Access Control System provides interactive API documentation through Swagger UI. This interactive documentation allows you to explore and test the API directly from your browser.')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Accessing Swagger UI', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'The Swagger UI documentation is available at:')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Production: https://api.onebee.com/docs/', 0, 1, 'L')
    pdf.cell(0, 10, 'Development: http://localhost:5000/docs/', 0, 1, 'L')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Features of Swagger UI', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    features = [
        '- Interactive API Testing: Try out API endpoints directly from the browser',
        '- Request/Response Examples: See example requests and responses for each endpoint',
        '- Authentication Integration: Test authenticated endpoints with your JWT token',
        '- Schema Definitions: View detailed models and data structures',
        '- OpenAPI Specification: Download the complete API specification in OpenAPI format',
        '- Real-time Validation: Validate your requests before sending them'
    ]
    for feature in features:
        pdf.cell(0, 10, feature, 0, 1, 'L')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'API Namespaces', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    namespaces = [
        'vehicle: Vehicle detection and ANPR operations',
        'barrier: Barrier control operations',
        'health: Hardware health check operations'
    ]
    for ns in namespaces:
        pdf.cell(0, 10, '- ' + ns, 0, 1, 'L')
    
    # Using Swagger UI
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '10. Using Swagger UI', 0, 1, 'L')
    pdf.ln(5)
    
    # Authentication
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Authentication in Swagger UI', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '1. Click the "Authorize" button at the top of the page\n2. Enter your JWT token in the format: Bearer <your_token>\n3. Click "Authorize"\n4. All subsequent requests will include your authentication token')
    
    # Testing Endpoints
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Testing Endpoints', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '1. Expand the endpoint you want to test by clicking on it\n2. Click the "Try it out" button\n3. Fill in the required parameters\n4. Click "Execute"\n5. View the response below the request')
    
    # Models
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Available Models', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    models = [
        'VehiclePresence: Vehicle detection data',
        'ANPRResult: ANPR recognition results',
        'BarrierControl: Barrier control commands',
        'User: User management data',
        'Location: Location management data',
        'Lane: Lane configuration data',
        'Device: Device management data',
        'AccessLog: Access log entries'
    ]
    for model in models:
        pdf.cell(0, 10, '- ' + model, 0, 1, 'L')
    
    # Authentication
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '3. Authentication', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'All API requests require authentication using a JWT token. Include the token in the Authorization header of your requests:')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Authorization: Bearer <your_token>', 0, 1, 'L')
    
    # Base URL
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '4. Base URL', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Production: https://api.onebee.com/v1', 0, 1, 'L')
    pdf.cell(0, 10, 'Development: http://localhost:5000/api', 0, 1, 'L')
    
    # API Endpoints
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '5. API Endpoints', 0, 1, 'L')
    
    # User Management
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.1 User Management', 0, 1, 'L')
    pdf.ln(5)
    
    # Get Users
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'GET /users', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Retrieves a list of all vehicle users.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'GET /api/users\nAuthorization: Bearer <your_token>')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Response:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''{
    "users": [
        {
            "id": 1,
            "name": "John Doe",
            "vehicle_number": "KA01AB1234",
            "fastag_id": "FASTAG1234",
            "location_id": 1,
            "valid_from": "2024-01-01",
            "valid_to": "2024-12-31",
            "is_active": true
        }
    ]
}''')
    
    # Add User
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'POST /users', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Creates a new vehicle user.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''POST /api/users
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "name": "Jane Doe",
    "vehicle_number": "MH02CD5678",
    "fastag_id": "FASTAG5678",
    "location_id": 2,
    "valid_from": "2024-01-01",
    "valid_to": "2024-12-31",
    "is_active": true
}''')
    
    # Location Management
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.2 Location Management', 0, 1, 'L')
    pdf.ln(5)
    
    # Get Locations
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'GET /locations', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Retrieves a list of all locations.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'GET /api/locations\nAuthorization: Bearer <your_token>')
    
    # Lane Management
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.3 Lane Management', 0, 1, 'L')
    pdf.ln(5)
    
    # Get Lanes
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'GET /lanes', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Retrieves a list of all lanes.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'GET /api/lanes\nAuthorization: Bearer <your_token>')
    
    # Device Management
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.4 Device Management', 0, 1, 'L')
    pdf.ln(5)
    
    # Get Devices
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'GET /devices', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Retrieves a list of all devices.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'GET /api/devices\nAuthorization: Bearer <your_token>')
    
    # Access Logs
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.5 Access Logs', 0, 1, 'L')
    pdf.ln(5)
    
    # Get Access Logs
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'GET /access-logs', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Retrieves a list of access logs with optional filtering.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''GET /api/access-logs?start_date=2024-01-01&end_date=2024-01-31&location_id=1
Authorization: Bearer <your_token>''')
    
    # Vehicle Management
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.6 Vehicle Management', 0, 1, 'L')
    pdf.ln(5)
    
    # Vehicle Presence
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'POST /vehicle/presence', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Report vehicle presence detection.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''POST /api/vehicle/presence
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "lane_id": 1,
    "device_id": 1,
    "timestamp": "2024-04-08T10:00:00",
    "confidence": 0.95
}''')
    
    # ANPR Result
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'POST /vehicle/anpr', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Process ANPR camera result.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''POST /api/vehicle/anpr
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "lane_id": 1,
    "device_id": 2,
    "vehicle_number": "KA01AB1234",
    "confidence": 0.98,
    "timestamp": "2024-04-08T10:00:01",
    "image_path": "/uploads/anpr/2024/04/08/image_001.jpg"
}''')
    
    # Barrier Management
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.7 Barrier Management', 0, 1, 'L')
    pdf.ln(5)
    
    # Barrier Control
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'POST /barrier/control', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Control barrier operation.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''POST /api/barrier/control
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "lane_id": 1,
    "device_id": 3,
    "action": "open",
    "timestamp": "2024-04-08T10:00:02"
}''')
    
    # Health Management
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5.8 Health Management', 0, 1, 'L')
    pdf.ln(5)
    
    # Health Check
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'POST /health/check', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Update device health status.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''POST /api/health/check
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "lane_id": 1,
    "device_id": 1,
    "device_type": "sensor",
    "status": "active",
    "last_heartbeat": "2024-04-08T10:00:00",
    "error_message": null
}''')
    
    # Health Status
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'GET /health/status/{lane_id}', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'Get health status of all devices in a lane.')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Request:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''GET /api/health/status/1
Authorization: Bearer <your_token>''')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Example Response:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''{
    "lane_id": 1,
    "lane_name": "Main Gate Lane 1",
    "devices": [
        {
            "device_id": 1,
            "device_type": "sensor",
            "status": "active",
            "last_heartbeat": "2024-04-08T10:00:00"
        },
        {
            "device_id": 2,
            "device_type": "anpr",
            "status": "active",
            "last_heartbeat": "2024-04-08T10:00:00"
        }
    ]
}''')
    
    # Response Codes
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '6. Response Codes', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    response_codes = [
        ('200', 'OK - Request successful'),
        ('201', 'Created - Resource created successfully'),
        ('400', 'Bad Request - Invalid request parameters'),
        ('401', 'Unauthorized - Invalid or missing authentication'),
        ('403', 'Forbidden - Insufficient permissions'),
        ('404', 'Not Found - Resource not found'),
        ('500', 'Internal Server Error - Server error occurred')
    ]
    for code, description in response_codes:
        pdf.cell(30, 10, code, 0, 0, 'L')
        pdf.cell(0, 10, description, 0, 1, 'L')
    
    # Error Handling
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '7. Error Handling', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'All errors are returned in the following format:')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": "Additional error details if available"
    }
}''')
    
    # Rate Limiting
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '8. Rate Limiting', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'API requests are limited to 1000 requests per hour per API key. Rate limit information is included in the response headers:')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1516131940''')
    
    # Examples
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '9. Examples', 0, 1, 'L')
    pdf.ln(5)
    
    # Python Example
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Python Example:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, '''import requests

# Set up the API client
api_key = 'your_api_key'
base_url = 'https://api.onebee.com/v1'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Get all users
response = requests.get(f'{base_url}/users', headers=headers)
users = response.json()

# Create a new user
new_user = {
    'name': 'John Doe',
    'vehicle_number': 'KA01AB1234',
    'fastag_id': 'FASTAG1234',
    'location_id': 1,
    'valid_from': '2024-01-01',
    'valid_to': '2024-12-31',
    'is_active': True
}

response = requests.post(f'{base_url}/users', headers=headers, json=new_user)
created_user = response.json()''')
    
    # Save the PDF
    pdf.output('Onebee_API_Documentation.pdf')

if __name__ == '__main__':
    generate_api_docs() 