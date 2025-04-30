# API Testing Guide

This guide provides detailed instructions for testing various API endpoints using the API Test page.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Health Check API](#health-check-api)
3. [Barrier Control API](#barrier-control-api)
4. [Vehicle Presence API](#vehicle-presence-api)
5. [Access Control API](#access-control-api)
6. [Troubleshooting](#troubleshooting)

## Getting Started

The API Test page provides a user-friendly interface to test all API endpoints. Each section includes:
- Request format details
- Example cURL commands
- Interactive testing form
- Response display area

## Health Check API

### Endpoint
```
POST /api/health/check
```

### Request Format
```json
{
    "lane_id": 1,
    "device_id": 1,
    "device_type": "sensor",
    "status": "active",
    "last_heartbeat": "2024-03-20T10:00:00Z",
    "error_message": null
}
```

### Testing Steps
1. Enter the Lane ID (e.g., 1)
2. Enter the Device ID (e.g., 1)
3. Select Device Type (sensor/anpr/controller)
4. Click "Send Health Check"

### Example cURL
```bash
curl -X POST http://localhost:5000/api/health/check \
  -H "Content-Type: application/json" \
  -d '{
    "lane_id": 1,
    "device_id": 1,
    "device_type": "sensor",
    "status": "active",
    "last_heartbeat": "2024-03-20T10:00:00Z"
  }'
```

## Barrier Control API

### Endpoint
```
POST /api/barrier/control
```

### Request Format
```json
{
    "lane_id": 1,
    "device_id": 1,
    "action": "open",
    "timestamp": "2024-03-20T10:00:00Z"
}
```

### Testing Steps
1. Enter the Lane ID
2. Enter the Device ID
3. Select Action (open/close)
4. Click "Send Command"

### Example cURL
```bash
curl -X POST http://localhost:5000/api/barrier/control \
  -H "Content-Type: application/json" \
  -d '{
    "lane_id": 1,
    "device_id": 1,
    "action": "open",
    "timestamp": "2024-03-20T10:00:00Z"
  }'
```

## Vehicle Presence API

### Endpoint
```
POST /api/vehicle/presence
```

### Request Format
```json
{
    "lane_id": 1,
    "device_id": 1,
    "timestamp": "2024-03-20T10:00:00Z",
    "confidence": 0.95
}
```

### Testing Steps
1. Enter the Lane ID
2. Enter the Device ID
3. Set Confidence Level (0.0 to 1.0)
4. Click "Send Presence Update"

### Example cURL
```bash
curl -X POST http://localhost:5000/api/vehicle/presence \
  -H "Content-Type: application/json" \
  -d '{
    "lane_id": 1,
    "device_id": 1,
    "timestamp": "2024-03-20T10:00:00Z",
    "confidence": 0.95
  }'
```

## Access Control API

### Endpoint
```
POST /api/access/control
```

### Request Format
```json
{
    "lane_id": 1,
    "device_id": 1,
    "vehicle_number": "KA01AB1234",
    "timestamp": "2024-03-20T10:00:00Z"
}
```

### Testing Steps
1. Enter the Lane ID
2. Enter the Device ID
3. Enter Vehicle Number
4. Click "Send Access Request"

### Example cURL
```bash
curl -X POST http://localhost:5000/api/access/control \
  -H "Content-Type: application/json" \
  -d '{
    "lane_id": 1,
    "device_id": 1,
    "vehicle_number": "KA01AB1234",
    "timestamp": "2024-03-20T10:00:00Z"
  }'
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the server is running
   - Check if the port is correct
   - Verify firewall settings

2. **Invalid Request Format**
   - Check all required fields are filled
   - Verify timestamp format (ISO 8601)
   - Ensure numeric values are within valid ranges

3. **Authentication Errors**
   - Verify API key is correct
   - Check token expiration
   - Ensure proper headers are set

### Response Codes

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### Testing Tips

1. **Start with Basic Tests**
   - Test with minimal required fields
   - Verify basic functionality before complex scenarios

2. **Use Valid Data**
   - Use existing lane and device IDs
   - Follow proper timestamp format
   - Use realistic confidence values

3. **Check Response Format**
   - Verify response structure
   - Check for error messages
   - Validate status codes

4. **Monitor Server Logs**
   - Check server console for errors
   - Review application logs
   - Monitor database operations

## Best Practices

1. **Test Environment**
   - Use a dedicated test environment
   - Keep test data separate from production
   - Reset test data periodically

2. **Data Validation**
   - Test with valid and invalid data
   - Verify error handling
   - Check boundary conditions

3. **Security**
   - Don't expose sensitive data
   - Use secure connections
   - Follow API security guidelines

4. **Documentation**
   - Keep test cases documented
   - Record any issues found
   - Update documentation as needed 