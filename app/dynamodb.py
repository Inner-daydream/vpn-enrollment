from webbrowser import get
import boto3
import botocore.exceptions
from boto3.dynamodb.conditions import Key
import bcrypt
import base64
import config
import flask_login
import flask

class User(flask_login.UserMixin):
    def __init__(self, id,session=flask.session):
        user_data = get_user(id)
        self.id = id
        print(user_data)
        self.admin = user_data['Admin']
        if session.get('user'):
            self.ms_user = True
            self.username = session['user']['name']
        else:
            self.ms_user = False
            self.username = user_data['Displayname']
        self.facial_recognition = session['facial_recognition']
        

config = config.AWSConfig
def create_users_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT)

    table = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'Id',
                'KeyType': 'HASH',
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table


def new_user(password=None,dynamodb=None,admin=False,Id=None,displayname = None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT)
    if password:
        password=base64.b64encode(password)
    table = dynamodb.Table('Users')
    response = table.put_item(
       Item={
            'Id': Id,
            'Password': password,
            'Admin': admin,
            'Displayname':displayname
       }
    )
    return response

def get_user(Id,dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT)
    table = dynamodb.Table('Users')
    try:
        response = table.get_item(Key={'Id' : Id})
    except botocore.exceptions.ClientError as e:
        print(e.response['Error']['Message'])
    if "Item" in response:
        return response['Item']
    else:
        raise ValueError("User not found")

def validate_login(Id,password,dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT)
        table = dynamodb.Table('Users')
    try:
        response = table.query(
            KeyConditionExpression = Key('Id').eq(Id)
        )
        with open('validate_login.log','w') as file:
            file.write(str(response))
        user_password = base64.b64decode(response['Items'][0]['Password'].value)
        password = bytes(password,'UTF-8')
        return bcrypt.checkpw(password,user_password)
    except IndexError:
        return False

def table_exists(client=None):
    if not client:
        client = boto3.client('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT) 
    try:
        client.describe_table(TableName='Users')
        return True
    except client.exceptions.ResourceNotFoundException:
        return False

