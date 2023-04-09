import json
import os
import boto3

KEY_ID = os.environ['KEY_ID']

# function definition
def lambda_handler(event, context):
    print(event)
    plain_text = event['text']
    print(plain_text)
    client = boto3.client('kms')
    cipher_text = KeyEncrypt(client).encrypt(plain_text, KEY_ID)
    print(cipher_text)
    encrypted_text_dict = {
        'encrypted_text': cipher_text
    }
    return {
        'statusCode': 200,
        'body': json.dumps(encrypted_text_dict)
    }


# Ref: https://docs.aws.amazon.com/code-library/latest/ug/python_3_kms_code_examples.html
class KeyEncrypt:
    def __init__(self, kms_client):
        self.kms_client = kms_client

    def encrypt(self, text, key_id):
        """
        Encrypts text by using the specified key.

        :param key_id: The ARN or ID of the key to use for encryption.
        :return: The encrypted version of the text.
        """
        cipher_text = self.kms_client.encrypt(KeyId=key_id, Plaintext=text.encode('utf-8'))['CiphertextBlob'].hex()
        return cipher_text
