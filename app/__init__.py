from flask import Flask
import config
from flask_session import Session
import app.dynamodb as dynamodb


app = Flask(__name__)
app.config.from_object(config.FlaskConfig)
Session(app)

from app import routes


if __name__ == "__main__":
     app.run(host="localhost", port=8080, debug=True)
     print('test1')

@app.before_first_request
def db_init():
     if not dynamodb.table_exists():
          dynamodb.create_users_table()
          dynamodb.new_user(Id=app.config['ADMIN_USERNAME'],password=app.config['ADMIN_PASSWORD'],admin=True)

          

