"""Provides a web app to manage wireguard"""
import time
import subprocess

import flask
import flask_login
import flask_session
import config
from app import wireguard_management, enroll, dynamodb

login_manager = flask_login.LoginManager()
app = flask.Flask(__name__)
app.config.from_object(config.FlaskConfig)
login_manager.init_app(app)
flask_session.Session(app)

from app import routes # pylint: disable=wrong-import-position

@app.before_first_request
def init():
    """Initiates the web app"""
    if dynamodb.table_exists():
        wireguard_management.retrieve_config()
    else:
        dynamodb.create_users_table()
        time.sleep(5)
        enroll.enroll_user(
        password=app.config['ADMIN_PASSWORD'],
        admin=True,email=app.config['ADMIN_USERNAME'],
        displayname="admin")
    subprocess.Popen(['wg-quick','up','wg0'])
