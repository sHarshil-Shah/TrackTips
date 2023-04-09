import json
import os
import boto3

KEY_ID = os.environ['KEY_ID']

# function definition
def lambda_handler(event, context):
    body = event #json.loads(event['body'])
    cipher_text = body['text']
    client = boto3.client('kms')
    plain_text = KeyEncrypt(client).decrypt(cipher_text, KEY_ID)
    plain_text_dict = {
        'decrypted_text': plain_text
    }
    return {
        'statusCode': 200,
        'body': json.dumps(plain_text_dict)
    }


# Ref: https://docs.aws.amazon.com/code-library/latest/ug/python_3_kms_code_examples.html
class KeyEncrypt:
    def __init__(self, kms_client):
        self.kms_client = kms_client
    
    def decrypt(self, encrypted_text, key_id):
        decrypted_text = self.kms_client.decrypt(CiphertextBlob=bytes.fromhex(encrypted_text), KeyId=key_id)['Plaintext'].decode('utf-8')
        return decrypted_text
