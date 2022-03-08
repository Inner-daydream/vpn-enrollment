from flask import Flask,session,render_template,url_for
import config
from flask_session import Session
import app.dynamodb as dynamodb
import flask_login

login_manager = flask_login.LoginManager()
app = Flask(__name__)
app.config.from_object(config.FlaskConfig)
login_manager.init_app(app)
Session(app)

from app import routes


if __name__ == "__main__":
     app.run(host="localhost", port=8080, debug=True)

@app.before_first_request
def db_init():
     if not dynamodb.table_exists():
          dynamodb.create_users_table()
          dynamodb.new_user(Id=app.config['ADMIN_USERNAME'],password=app.config['ADMIN_PASSWORD'],admin=True)
