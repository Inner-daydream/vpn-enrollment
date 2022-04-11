import flask
import app.wireguard_management as wireguard_management
import config
import app.enroll as enroll
import flask_session
import app.dynamodb as dynamodb
import flask_login
import time
import subprocess

login_manager = flask_login.LoginManager()
app = flask.Flask(__name__)
app.config.from_object(config.FlaskConfig)
login_manager.init_app(app)
flask_session.Session(app)

from app import routes

@app.before_first_request
def init():
     if dynamodb.table_exists():
          wireguard_management.retrieve_config()
     else:
          dynamodb.create_users_table()
          time.sleep(5)
          enroll.enroll_user(password=app.config['ADMIN_PASSWORD'],admin=True,email=app.config['ADMIN_USERNAME'],displayname="admin")
     subprocess.Popen(['wg-quick','up','wg0'])

          