# Access Control System

A comprehensive access control system for managing vehicle entry/exit in facilities.

## Features

- User Management
- Location Management
- Lane Management
- Device Management (ANPR, Fastag, Gate Controllers)
- Real-time Access Control
- Comprehensive Reporting
- API Integration

## Tech Stack

- Python 3.9+
- Flask
- SQLAlchemy
- Bootstrap 5
- SQLite

## Directory Structure

```
access-control/
├── app.py              # Main application file
├── api.py              # API routes
├── models.py           # Database models
├── wsgi.py            # WSGI entry point
├── requirements.txt    # Python dependencies
├── migrations/         # Database migrations
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
└── uploads/           # User uploads directory
```

## Deployment on PythonAnywhere

1. Create a new account on PythonAnywhere (if you haven't already)

2. Open a Bash console and clone your repository:
   ```bash
   git clone <your-repo-url>
   cd access-control
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Configure your web app in PythonAnywhere:
   - Go to the Web tab
   - Add a new web app
   - Choose Manual Configuration
   - Choose Python 3.9
   - Set the following paths:
     - Source code: /home/<username>/access-control
     - Working directory: /home/<username>/access-control
     - WSGI configuration file: /var/www/<username>_pythonanywhere_com_wsgi.py

5. Update the WSGI configuration file with:
   ```python
   import sys
   import os
   
   path = '/home/<username>/access-control'
   if path not in sys.path:
       sys.path.append(path)
   
   from wsgi import application
   ```

6. Set up environment variables in the Web tab:
   - SECRET_KEY
   - SQLALCHEMY_DATABASE_URI
   - FLASK_ENV

7. Initialize the database:
   ```bash
   flask db upgrade
   python init_db.py
   ```

8. Create uploads directory:
   ```bash
   mkdir uploads
   chmod 755 uploads
   ```

9. Reload your web app in PythonAnywhere

## Local Development

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd access-control
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in .env file:
   ```
   SECRET_KEY=your-secret-key-here
   SQLALCHEMY_DATABASE_URI=sqlite:///access_control.db
   FLASK_ENV=development
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   python init_db.py
   ```

6. Run the application:
   ```bash
   python app.py
   ```

## Default Admin Credentials

- Username: admin
- Password: admin123

*Make sure to change these credentials in production!*

## License

Copyright © 2024 Onebee Technology Pvt Ltd. All rights reserved. 