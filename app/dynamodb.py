"""Provides database interaction"""
import base64
import bcrypt

import boto3
import botocore.exceptions
from boto3.dynamodb.conditions import Key

import flask_login
import flask

import config



Config = config.AWSConfig

class User(flask_login.UserMixin):
    """User class used by flask_login"""
    def __init__(self, id,session=flask.session):
        user_data = get_user(id)
        self.id = id
        self.admin = user_data['Admin']
        if session.get('user'):
            self.ms_user = True
            self.username = session['user']['name']
        else:
            self.ms_user = False
            self.username = user_data['Displayname']
        self.facial_recognition = session['facial_recognition']

def add_peer(id,peer_name,public_key,allowed_ips,dynamodb=None):
    """Register a peer in the database"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
    table = dynamodb.Table('Users')
    response = table.update_item(
        Key={
            "Id": id
        },
        UpdateExpression="set #AttributeName.#NestedAttributeName=:p",
        ExpressionAttributeNames={
            "#NestedAttributeName": peer_name,
            "#AttributeName": "Peers"
        },
        ConditionExpression = "attribute_not_exists(#AttributeName.#NestedAttributeName)",
        ExpressionAttributeValues={
            ':p': {
                "Public_key": public_key,
                "AllowedIPs": allowed_ips,
                "Description": peer_name
            }
        },
        ReturnValues="UPDATED_NEW"
    )
    return response
def remove_peer(id,peer_name,dynamodb=None):
    """Remove a peer from the database"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
    table = dynamodb.Table('Users')
    response = table.update_item(
        Key={
            "Id": id
        },
        UpdateExpression="remove #AttributeName.#NestedAttributeName",
        ExpressionAttributeNames={
            "#NestedAttributeName": peer_name,
            "#AttributeName": "Peers"
        },
        ConditionExpression = "attribute_exists(#AttributeName.#NestedAttributeName)",
        ReturnValues="UPDATED_NEW"
    )
    return response
def get_peers(id,dynamodb=None):
    """Get a user peer list"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
    table = dynamodb.Table('Users')
    try:
        response = table.get_item(
            Key={'Id' : id},
            ProjectionExpression="Peers"
        )
    except botocore.exceptions.ClientError as exception:
        print(exception.response['Error']['Message'])
    if "Item" in response:
        return response['Item']['Peers']

def create_users_table(dynamodb=None):
    """Init the dynamodb table"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)

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
    """Register a new user in the database"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
    if password:
        password=base64.b64encode(password)
    table = dynamodb.Table('Users')
    response = table.put_item(
       Item={
            'Id': Id,
            'Password': password,
            'Admin': admin,
            'Displayname':displayname,
            'Peers': {}
       }
    )
    return response

def get_user(Id,dynamodb=None):
    """get an user by id"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
    table = dynamodb.Table('Users')
    try:
        response = table.get_item(Key={'Id' : Id})
    except botocore.exceptions.ClientError as exception:
        print(exception.response['Error']['Message'])
    if "Item" in response:
        return response['Item']
    else:
        raise ValueError("User not found")

def validate_login(Id,password,dynamodb=None):
    """Checks if an user credentials are correct"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
        table = dynamodb.Table('Users')
    try:
        response = table.query(
            KeyConditionExpression = Key('Id').eq(Id)
        )
        with open('validate_login.log','w', encoding='UTF-8') as file:
            file.write(str(response))
        user_password = base64.b64decode(response['Items'][0]['Password'].value)
        password = bytes(password,'UTF-8')
        return bcrypt.checkpw(password,user_password)
    except IndexError:
        return False

def table_exists(client=None):
    """Check if the Users table exists"""
    if not client:
        client = boto3.client('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
    try:
        client.describe_table(TableName='Users')
        return True
    except client.exceptions.ResourceNotFoundException:
        return False
