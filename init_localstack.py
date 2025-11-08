"""
Initialize LocalStack Resources

Creates Kinesis streams and DynamoDB table for the Bedside Monitor system.
"""

import os
os.environ['USE_LOCALSTACK'] = 'true'

from localstack_config import get_kinesis_client, get_dynamodb_resource

print("🚀 Initializing LocalStack resources for Bedside Monitor...\n")

# Get clients
kinesis = get_kinesis_client()
dynamodb = get_dynamodb_resource()

# ============================================================================
# CREATE KINESIS STREAMS
# ============================================================================
print("📊 Creating Kinesis Data Streams...")

streams = [
    ('BSMStream', 'Used by consumer_and_anomaly_detector.py'),
    ('BSM_Stream', 'Used by consume_and_update.py'),
    ('BSM_Data_Stream1', 'Used by local_consumer.py')
]

for stream_name, description in streams:
    try:
        kinesis.create_stream(StreamName=stream_name, ShardCount=1)
        print(f"   ✅ Created stream: {stream_name} - {description}")
    except kinesis.exceptions.ResourceInUseException:
        print(f"   ⚠️  Stream {stream_name} already exists")
    except Exception as e:
        print(f"   ❌ Error creating {stream_name}: {e}")

# ============================================================================
# CREATE DYNAMODB TABLE
# ============================================================================
print("\n💾 Creating DynamoDB Table...")

try:
    table = dynamodb.create_table(
        TableName='BSM_anamoly',
        KeySchema=[
            {'AttributeName': 'deviceid', 'KeyType': 'HASH'},
            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'deviceid', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print(f"   ✅ Created table: BSM_anamoly")
except dynamodb.meta.client.exceptions.ResourceInUseException:
    print(f"   ⚠️  Table BSM_anamoly already exists")
except Exception as e:
    print(f"   ❌ Error creating table: {e}")

# ============================================================================
# VERIFY RESOURCES
# ============================================================================
print("\n🔍 Verifying created resources...")

# List Kinesis streams
try:
    response = kinesis.list_streams()
    print(f"\n📊 Kinesis Streams ({len(response['StreamNames'])} total):")
    for stream in response['StreamNames']:
        print(f"   - {stream}")
except Exception as e:
    print(f"   ❌ Error listing streams: {e}")

# List DynamoDB tables
try:
    tables = list(dynamodb.tables.all())
    print(f"\n💾 DynamoDB Tables ({len(tables)} total):")
    for table in tables:
        print(f"   - {table.name}")
except Exception as e:
    print(f"   ❌ Error listing tables: {e}")

print("\n✅ LocalStack initialization complete!")
print("🌐 LocalStack is running at: http://localhost:4566")
print("\n📝 Next steps:")
print("   1. Start publisher: python kinesis_publisher_local.py")
print("   2. Start consumer: python consumer_and_anomaly_detector_local.py")
print("   3. Start DynamoDB writer: python consume_and_update_local.py\n")
