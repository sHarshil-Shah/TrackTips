import json
from fyers_api import accessToken
import boto3
from botocore.exceptions import ClientError
import os


def get_secret():
    secret_name = os.environ['secret_name'] #"fyers_api_details"
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

def lambda_handler(event, context):

    print('redirect url from environment ' + os.environ['redirect_uri'])
    secret = get_secret()

    session = accessToken.SessionModel(
        client_id=secret['client_id'],
        secret_key=secret['secret_key'],
        redirect_uri=os.environ['redirect_uri'], #'https://8ryr8gtl03.execute-api.us-east-1.amazonaws.com/prod',
        response_type='code'
    )
    
    response = session.generate_authcode()
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }