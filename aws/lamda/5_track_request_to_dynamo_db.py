import json
import uuid
import boto3
from datetime import date
import urllib.request
import os

# LAMBDA TEST
# "body": "{\"user_id\": \"<user_id>\", \"symbol\": \"testSymbol\",  \"target_date\": \"today\",\"target_price\": 3500}",
def lambda_handler(event, context):
    print(json.loads(event['body']))
    body = json.loads(event['body'])
    user_id = body['user_id']

    NSE_LINK = os.environ['NSE_FILE_URL']

    with urllib.request.urlopen(NSE_LINK) as file:
        contents = file.read().decode('utf-8')

    response = {}

    for line in contents.split('\n'):
        line = line.split(",")
        try:
            if body['symbol'] == line[9]:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(os.environ['track_list_dynamodb_table_name'])
                response = table.put_item(
                    Item=
                    {
                        'track_id': str(uuid.uuid1()),
                        'user_id': user_id,
                        "symbol": body['symbol'],
                        "target_date": body['target_date'],
                        "target_price": body['target_price'],
                        "start_date": str(date.today()),
                        "is_target_achieved": False
                    }
                )
                break
        except Exception:
            pass
    return {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode'] if response != {} else 422
    }
