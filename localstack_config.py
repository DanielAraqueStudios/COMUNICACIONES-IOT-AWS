"""
LocalStack Configuration Module

This module provides configuration for connecting to LocalStack
instead of AWS production services. It automatically detects if
running in local development mode and adjusts endpoints accordingly.

Usage:
    from localstack_config import get_kinesis_client, get_dynamodb_resource
    
    kinesis = get_kinesis_client()
    dynamodb = get_dynamodb_resource()
"""

import os
import boto3
from botocore.config import Config

# LocalStack endpoint
LOCALSTACK_ENDPOINT = os.getenv('LOCALSTACK_ENDPOINT', 'http://localhost:4566')

# Check if running in LocalStack mode
USE_LOCALSTACK = os.getenv('USE_LOCALSTACK', 'true').lower() == 'true'


def get_endpoint_url():
    """
    Get the appropriate endpoint URL based on environment.
    
    Returns:
        str: LocalStack endpoint if USE_LOCALSTACK=true, None for AWS
    """
    if USE_LOCALSTACK:
        print(f"🔧 Using LocalStack endpoint: {LOCALSTACK_ENDPOINT}")
        return LOCALSTACK_ENDPOINT
    else:
        print("☁️  Using AWS production endpoints")
        return None


def get_kinesis_client():
    """
    Create a Kinesis client configured for LocalStack or AWS.
    
    Returns:
        boto3.client: Configured Kinesis client
    """
    endpoint_url = get_endpoint_url()
    
    if USE_LOCALSTACK:
        # LocalStack configuration
        return boto3.client(
            'kinesis',
            endpoint_url=endpoint_url,
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1',
            config=Config(
                signature_version='s3v4',
                retries={'max_attempts': 3}
            )
        )
    else:
        # AWS production configuration
        return boto3.client('kinesis', region_name='us-east-1')


def get_dynamodb_resource():
    """
    Create a DynamoDB resource configured for LocalStack or AWS.
    
    Returns:
        boto3.resource: Configured DynamoDB resource
    """
    endpoint_url = get_endpoint_url()
    
    if USE_LOCALSTACK:
        # LocalStack configuration
        return boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1',
            config=Config(
                signature_version='s3v4',
                retries={'max_attempts': 3}
            )
        )
    else:
        # AWS production configuration
        return boto3.resource('dynamodb', region_name='us-east-1')


def put_kinesis_record(stream_name, data, partition_key='default'):
    """
    Put a record into a Kinesis stream.
    
    Args:
        stream_name (str): Name of the Kinesis stream
        data (str): JSON string data to put
        partition_key (str): Partition key for the record
    
    Returns:
        dict: Response from Kinesis PutRecord operation
    """
    client = get_kinesis_client()
    
    try:
        response = client.put_record(
            StreamName=stream_name,
            Data=data,
            PartitionKey=partition_key
        )
        print(f"✅ Published to {stream_name}: {data}")
        return response
    except Exception as e:
        print(f"❌ Error publishing to Kinesis: {e}")
        raise


# Example usage and testing
if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("🧪 Testing LocalStack Configuration\n")
    
    # Test Kinesis client
    print("1️⃣ Testing Kinesis client...")
    kinesis = get_kinesis_client()
    try:
        streams = kinesis.list_streams()
        print(f"   Available streams: {streams.get('StreamNames', [])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test DynamoDB resource
    print("2️⃣ Testing DynamoDB resource...")
    dynamodb = get_dynamodb_resource()
    try:
        tables = list(dynamodb.tables.all())
        print(f"   Available tables: {[table.name for table in tables]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test putting a record
    print("3️⃣ Testing Kinesis put_record...")
    test_data = {
        'deviceid': 'BSM_G101',
        'timestamp': str(datetime.now()),
        'datatype': 'HeartRate',
        'value': 85
    }
    
    try:
        put_kinesis_record(
            stream_name='BSM_Stream',
            data=json.dumps(test_data),
            partition_key='BSM_G101'
        )
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Configuration test complete!")
