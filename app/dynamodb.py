import boto3
import botocore.exceptions
import config


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


def new_user(password=None,dynamodb=None,admin=False,Id=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT)

    table = dynamodb.Table('Users')
    response = table.put_item(
       Item={
            'Id': Id,
            'Password': password,
            'Admin': admin
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

def table_exists(client=None):
    if not client:
        client = boto3.client('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT) 
    try:
        client.describe_table(TableName='Users')
        return True
    except client.exceptions.ResourceNotFoundException:
        return False

