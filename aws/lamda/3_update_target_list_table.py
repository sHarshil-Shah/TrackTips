import json
import boto3
import os
from datetime import date

# LAMBDA TEST
# "{\"user_id\":\"user_id\"}"

# REST TEST
# {"user_id":"user_id"}

def update_target_achieved(track_id, user_id):
    dynamodb = boto3.resource('dynamodb')
    print("table name: ", os.environ['track_list_dynamodb_table_name'])
    table = dynamodb.Table(os.environ['track_list_dynamodb_table_name'])

    response = table.update_item(
        Key={
            'track_id': track_id,
            'user_id': user_id
        },
        UpdateExpression="set #is_target_achieved=:achieved",
        ExpressionAttributeNames={
            '#is_target_achieved': 'is_target_achieved'
        },
        ExpressionAttributeValues={
            ':achieved': True
        },
        ReturnValues="UPDATED_NEW"
    )

    print("UpdateItem succeeded for track_id:", track_id)
    return response


def check_for_update(client_id, item, user_id):
    lambda_client = boto3.client('lambda')

    inputParams = {
        "user_id": user_id,
        "client_id": client_id,
        "range_from": item['start_date'],
        "range_to": item['target_date'],
        "target_price": int(item['target_price']),
        "symbol": item['symbol']
    }

    invoke_response = lambda_client.invoke(
        FunctionName=os.environ['check_target_lambda_ARN'],
        InvocationType='RequestResponse',
        Payload=json.dumps(inputParams)
    )

    payload = json.loads(invoke_response['Payload'].read().decode("utf-8"))
    print(payload)
    response_payload = json.loads(payload['body'])
    print("response from another lambda")
    print(response_payload)
    return response_payload['is_target_achieved']

def get_client_id():
    secret_name = os.environ['secret_name']  # "fyers_api_details"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # try:
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    # except ClientError as e:
    #     # For a list of exceptions thrown, see
    #     # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    #     raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    return json.loads(secret)['client_id']



def traverse_table_to_check_update(user_id):
    # Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/paginator/Query.html
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['track_list_dynamodb_table_name'])

    response = table.scan(
        FilterExpression='#na >= :val and #ia = :is_target_achieved and #user_id = :user_id',
        ExpressionAttributeNames={
            '#na': 'target_date',
            '#ia': 'is_target_achieved',
            '#user_id': 'user_id'
        },
        ExpressionAttributeValues={
            ':val': str(date.today()),
            ':is_target_achieved': False,
            ':user_id': user_id
        }
    )
    # print(response)
    items = response['Items']
    print(items)
    return items

# def get_access_token(user_id):
#     lambda_client = boto3.client('lambda')

#     inputParams = {
#         "user_id": user_id
#     }

#     invoke_response = lambda_client.invoke(
#         FunctionName=os.environ['GetDecryptedAccessCodeLambda_ARN'],
#         InvocationType='RequestResponse',
#         Payload=json.dumps(inputParams)
#     )

#     payload = json.loads(invoke_response['Payload'].read().decode("utf-8"))
#     print(payload)
#     response_payload = json.loads(payload['body'])
#     print("response from another lambda")
#     print(response_payload)
#     return response_payload['access_token']


def lambda_handler(event, context):
    body = json.loads(event['body'])
    print(body)
    print(type(body))
    items = traverse_table_to_check_update(body['user_id'])
    client_id = get_client_id()
    
    for item in items:
        is_target_achieved = check_for_update(client_id, item, body['user_id'])
        print(is_target_achieved)
        if is_target_achieved:
            response = update_target_achieved(item['track_id'], item['user_id'])

    return {
        'statusCode': 200
    }
