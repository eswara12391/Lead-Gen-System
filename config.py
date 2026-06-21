import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# MySQL Database configuration - Support environment variables for server deployment
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')  # Empty for XAMPP, set env var on server
MYSQL_DB = os.environ.get('MYSQL_DB', 'linkedin_lead_db')  # Database name
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3308))  # Default MySQL port, configurable for server
MYSQL_CURSORCLASS = 'DictCursor'  # Use DictCursor class name
MYSQL_USE_UNICODE = True
MYSQL_CHARSET = 'utf8mb4'

# Database connection pool settings
MYSQL_CONNECTION_TIMEOUT = int(os.environ.get('MYSQL_CONNECTION_TIMEOUT', 30))

# Google Gemini AI Configuration (Free - Get key from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')