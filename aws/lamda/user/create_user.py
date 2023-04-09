import json
import boto3
import os


# {'email': 'sharshil1299@gmail.com', 'password': 'myp@ss12'}

####### Lambda Test Event
# {
#   "body": "{\n  \"email\": \"sharshil1299@gmail.com\",\n \"password\": \"myp@ss12\"\n}",
#   "httpMethod": "POST",
#   "path": "/"
# }

# function definition
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    # Define the client to interact with AWS Lambda
    # lambdaFunc = boto3.client('lambda')
    print(event)
    # print(event['body'])
    body = event

    # inputParams = {
    #     "text": body['access_token']
    # }

    # lambda_client = boto3.client('lambda')
    # invoke_response = lambda_client.invoke(
    #     FunctionName=os.environ['encryption_lambda_ARN'],
    #     InvocationType='RequestResponse',
    #     Payload=json.dumps(inputParams)
    # )

    # response_payload = json.loads(json.loads(invoke_response['Payload'].read().decode("utf-8"))['body'])
    # print(response_payload)
    # encrypted_access_token = response_payload['encrypted_text']

    table = dynamodb.Table(os.environ['user_dynamodb_table_name'])
    # inserting values into table
    response = table.put_item(
        Item=
        {
            "user_id": body['user_id'],
            "access_token": json.loads(body['encrypted_text']['Payload']['body'])['encrypted_text']
        }
    )

    print(response)
    return {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode']
    }
