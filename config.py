"""Provides config classes"""
import os
class FlaskConfig:
    """Contains the flask app config"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    AUTHORITY = os.environ.get('AUTHORITY') \
    or "https://login.microsoftonline.com/49f7e826-1d46-4fd2-a3ca-a43422c8f815"
    REDIRECT_PATH = "/getAToken"
    GRAPH_ENDPOINT = os.environ.get('GRAPH_ENDPOINT') or 'https://graph.microsoft.com/v1.0/users'
    SCOPE = os.environ.get('SCOPE') or ["User.ReadBasic.All"]
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or "filesystem"
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or "contact@lucasquitman.fr"
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
class AWSConfig:
    """Contains the AWS config"""
    DYNAMODB_ENDPOINT = os.environ.get('DYNAMODB_ENDPOINT')
class WireGuardConfig:
    """Contains the wireguard config"""
    DNS = os.environ.get('DNS') or "1.1.1.1"
    PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
    SERVER_SUBNET = os.environ.get('SERVER_SUBNET') or "10.200.200.0/24"
    SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS') or "10.200.200.1"
    SERVER_DESCRIPTION = os.environ.get('SERVER_DESCRIPTION') or "VPN Main"
    TEMP_CONFIG_PATH =  os.environ.get('TEMP_CONFIG_PATH') or "/tmp"
    PRODUCTION_CONFIG_PATH = os.environ.get('PRODUCTION_CONFIG_PATH') \
    or "/Users/sibelius/Tech/vpn/wg-config/server"
    DOWNLOAD_CONFIG_PATH = os.environ.get('DOWNLOAD_CONFIG_PATH') or "./static/download"
    ENDPOINT = os.environ.get('ENDPOINT')
    KEEPALIVE = os.environ.get('KEEPALIVE') or "25"
    ALLOWED_IPS= os.environ.get('ALLOWED_IPS') or "0.0.0.0/0"
    NET_INTERFACE=os.environ.get('NET_INTERFACE') or "eth0"
