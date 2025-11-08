import boto3
import time
import json

client = boto3.client('kinesis')
shardIterator = client.get_shard_iterator(
    StreamName='BSMStream',
    ShardId='shardId-000000000000',
    ShardIteratorType='LATEST',
)['ShardIterator']

while True:
    response = client.get_records(
        ShardIterator=shardIterator
    )
    shardIterator = response['NextShardIterator']
    if len(response['Records']) > 0:
        for item in response['Records']:
            readings = json.loads(item["Data"])
        print(readings)

        if (readings['datatype'] == 'HeartRate') and ((60 > int(readings['value'])) or (int(readings['value']) > 100)):
            print("Anomaly detected")
        elif (readings['datatype'] == 'SPO2') and ((85 > int(readings['value'])) or (int(readings['value']) > 110)):
            print("Anomaly detected")
        elif (readings['datatype'] == 'Temperature') and ((96 > int(readings['value'])) or (int(readings['value']) > 101)):
            print("Anomaly detected")
    time.sleep(0.2)
