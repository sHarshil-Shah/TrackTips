import boto3
import os
import json


def get_encrypted_access_token_from_db(user_id):
    # Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/paginator/Query.html
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['users_table_name'])
    # Ref: https://stackoverflow.com/a/59426921
    # decoded = jwt.decode(access_token, options={"verify_signature": False})  # works in PyJWT >= v2.0
    # print(decoded)
    response = table.scan(
        FilterExpression='#user_id = :user_id',
        ExpressionAttributeNames={
            '#user_id': 'user_id'
        },
        ExpressionAttributeValues={
            ':user_id': user_id
        }
    )
    # print(response)
    items = response['Items']
    print(items)
    return items[0]['access_token']

def decrypt_access_token(access_token):
    lambda_client = boto3.client('lambda')

    inputParams = {
        "text": access_token
    }

    invoke_response = lambda_client.invoke(
        FunctionName=os.environ['DecryptionUsingKMSLambda_ARN'],
        InvocationType='RequestResponse',
        Payload=json.dumps(inputParams)
    )

    payload = json.loads(invoke_response['Payload'].read().decode("utf-8"))
    print(payload)
    response_payload = json.loads(payload['body'])
    print("response from another lambda")
    print(response_payload)
    return response_payload['decrypted_text']


def lambda_handler(event, context):
    print(event)
    body = event #json.loads(event['body'])
    user_id = body['user_id']
    
    encrypted_access_token = get_encrypted_access_token_from_db(user_id)
    decrypted_access_token = decrypt_access_token(encrypted_access_token)
    
    response = {}
    response['access_token'] = decrypted_access_token
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }