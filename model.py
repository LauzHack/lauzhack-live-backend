import flask.json
import boto3

from decimal import Decimal
import html
import os
import time
import uuid

TABLE_NAME = 'messages'


class DecimalJSONEncoder(flask.json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert decimal instances to strings.
            return float(obj)
        return super(DecimalJSONEncoder, self).default(obj)


class Model:
    def __init__(self):
        if os.environ.get('LOCAL_DYNAMO', '0') == '1':
            self.dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
        else:
            self.dynamodb = boto3.resource('dynamodb')
        try:
            table = self.dynamodb.create_table(
                TableName=TABLE_NAME,
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            table.meta.client.get_waiter('table_exists').wait(TableName=TABLE_NAME)
        except:
            print('table already exists')

    def get(self):
        table = self.dynamodb.Table(TABLE_NAME)
        results = table.scan()
        return results.get('Items')

    def put(self, message):
        table = self.dynamodb.Table(TABLE_NAME)
        message_id = str(uuid.uuid4())
        table.put_item(
            Item={
                'id': message_id,
                'timestamp': Decimal(time.time()),
                'text': html.escape(message, quote=False),
            }
        )
        return message_id

    def delete(self, id):
        table = self.dynamodb.Table(TABLE_NAME)
        table.delete_item(
            Key={
                'id': id
            }
        )
