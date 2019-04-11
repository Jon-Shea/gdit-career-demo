import json
from pprint import pprint
import boto3
dynamo_client = boto3.client("dynamodb")
table_name = "MessageLogTable"

def lambda_handler(event, context):
    pprint(event)
    records = event['Records']
    for record in records:
        sns = record["Sns"]
        body = json.loads(sns["Message"])
        message = body["message"]
        group_id = body["group_id"]
        timestamp = body["timestamp"]
        language = body["language"]

        message_digest = hash("{}{}{}{}".format(message, group_id, timestamp, language))

        item = {
            "message_digest": {"N": str(message_digest)},
            "group_id": {"N": str(group_id)},
            "timestamp": {"S": timestamp},
            "message": {"S": message},
            "language": {"S": language}
        }

        dynamo_client.put_item(TableName=table_name, Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps('logged messages to dynamodb')
    }