import os
class FlaskConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    AUTHORITY = os.environ.get('AUTHORITY') or "https://login.microsoftonline.com/49f7e826-1d46-4fd2-a3ca-a43422c8f815"
    REDIRECT_PATH = "/getAToken"
    ENDPOINT = os.environ.get('ENDPOINT') or 'https://graph.microsoft.com/v1.0/users'
    SCOPE = os.environ.get('ENDPOINT') or ["User.ReadBasic.All"]
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or "filesystem"
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or "admin"
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
class AWSConfig(object):
    DYNAMODB_ENDPOINT = os.environ.get('DYNAMODB_ENPOINT') or "http://localhost:8000"