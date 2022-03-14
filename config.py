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
class WireGuardConfig(object):
    SERVER_SUBNET = os.environ.get('SERVER_SUBNET') or "10.200.200.0/24"
    SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS') or "10.200.200.1"
    SERVER_DESCRIPTION = os.environ.get('SERVER_DESCRIPTION') or "VPN Main"
    TEMP_CONFIG_PATH =  os.environ.get('TEMP_CONFIG_PATH') or "/tmp"
    PRODUCTION_CONFIG_PATH = os.environ.get('PRODUCTION_CONFIG_PATH') or "/Users/sibelius/Tech/vpn/wg-config/server"
    DOWNLOAD_CONFIG_PATH = os.environ.get('DOWNLOAD_CONFIG_PATH') or "./static/download"
    ENDPOINT = os.environ.get('ENDPOINT')
    KEEPALIVE = os.environ.get('KEEPALIVE') or "25"