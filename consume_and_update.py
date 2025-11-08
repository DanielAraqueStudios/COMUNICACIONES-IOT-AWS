import boto3
import time
import json
from decimal import Decimal

# Get the service resource.
dynamodb = boto3.resource('dynamodb')

# Instantiate a table resource object without actually
# creating a DynamoDB table. Note that the attributes of this table
# are lazy-loaded: a request is not made nor are the attribute
# values populated until the attributes
# on the table resource are accessed or its load() method is called.
table = dynamodb.Table('BSM_anamoly')

client = boto3.client('kinesis')
shardIterator = client.get_shard_iterator(
    StreamName='BSM_Stream',
    ShardId='shardId-000000000003',
    ShardIteratorType='LATEST',
)['ShardIterator']

while True:
    response = client.get_records(
        ShardIterator=shardIterator
    )
    shardIterator = response['NextShardIterator']
    if len(response['Records']) > 0:
        for item in response['Records']:
            readings = json.loads(item["Data"], parse_float=Decimal)
        print(readings)

        if (readings['datatype'] == 'HeartRate') and ((60 > int(readings['value'])) or (int(readings['value']) > 100)):
            table.put_item(Item=readings)
            print("Anomaly detected, entry added in DynamoDB Table")
        elif (readings['datatype'] == 'SPO2') and ((85 > int(readings['value'])) or (int(readings['value']) > 110)):
            table.put_item(Item=readings)
            print("Anomaly detected, entry added in DynamoDB Table")
        elif (readings['datatype'] == 'Temperature') and ((96 > int(readings['value'])) or (int(readings['value']) > 101)):
            table.put_item(Item=readings)
            print("Anomaly detected, entry added in DynamoDB Table")
    time.sleep(0.2)
