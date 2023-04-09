import json

from botocore.exceptions import ClientError
from fyers_api import accessToken
import os
import boto3
import jwt

redirect_uri = ''  # os.environ['redirect_uri'] #'https://8ryr8gtl03.execute-api.us-east-1.amazonaws.com/prod'
response_type = 'code'
grant_type = 'authorization_code'


def get_secret():
    secret_name = os.environ['secret_name']  # "fyers_api_details"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    return json.loads(secret)


def call_step_function(access_token):
    client = boto3.client('stepfunctions')
    user_id = jwt.decode(access_token, options={"verify_signature": False})['fy_id']
    response = client.start_execution(
        stateMachineArn=os.environ['state_machine_arn'],
        input=json.dumps({'user_id': user_id, 'access_token': access_token, 'encryptionUsingKMSARN': os.environ['encryptionUsingKMSARN'], 'userCreationARN': os.environ['userCreationARN']}))
    print(response)
    return user_id


def lambda_handler(event, context):
    auth_code = event['queryStringParameters']['auth_code']
    secret = get_secret()

    session = accessToken.SessionModel(
        client_id=secret['client_id'],
        secret_key=secret['secret_key'],
        redirect_uri=redirect_uri,
        response_type=response_type,
        grant_type=grant_type
    )

    session.set_token(auth_code)
    response = session.generate_token()
    print(response)
    access_token = response["access_token"]
    user_id = call_step_function(access_token)
    return {
        'statusCode': 200,
        'body': json.dumps(user_id)
    }
