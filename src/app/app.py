import os
import boto3
import uuid
import json

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')

def handler(event, context):
    table = dynamodb.Table(table_name)
    record_id = event.get('id', str(uuid.uuid4()))
    
    table.put_item(
        Item={
            'id': record_id,
            'payload': event.get('payload', 'Default localstack payload')
        }
    )
    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Record inserted", "id": record_id})
    }