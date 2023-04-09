import json
from fyers_api import accessToken
from fyers_api import fyersModel
from datetime import datetime
import boto3
import os

# LAMBDA TEST
#   "{\"symbol\": \"testSymbol\",  \"target_date\": \"today\",\"target_price\": 3500}"

# REST TEST
# {
#     "symbol": "NSE:ADANITRANS-EQ",
#     "target_date": "2023-04-11",
#     "target_price": 450
# }

def get_access_token(user_id):
    lambda_client = boto3.client('lambda')

    inputParams = {
        "user_id": user_id
    }

    invoke_response = lambda_client.invoke(
        FunctionName=os.environ['GetDecryptedAccessCodeLambda_ARN'],
        InvocationType='RequestResponse',
        Payload=json.dumps(inputParams)
    )

    payload = json.loads(invoke_response['Payload'].read().decode("utf-8"))
    print(payload)
    response_payload = json.loads(payload['body'])
    print("response from another lambda")
    print(response_payload)
    return response_payload['access_token']



def lambda_handler(event, context):
    body = event
    print(event)
    access_token = get_access_token(body['user_id'])
    client_id = body['client_id']
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token)
   
    data = {"symbol": body['symbol'], "resolution": "D", "date_format": "1", "range_from": body['range_from'],
            "range_to": body['range_to'],#str(date.today()+1), 
            "cont_flag": "1"}
    print(data)
    data = fyers.history(data)
    print(data)
    response = {}
    response['is_target_achieved'] = False
    if data['s'] == "ok":
        for day in data['candles']:
            print(day)
            if day[3] <= int(body['target_price']) <= day[2]:
                response['is_target_achieved'] = True
                break
    print(response)
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }