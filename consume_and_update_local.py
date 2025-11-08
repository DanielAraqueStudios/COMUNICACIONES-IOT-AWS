"""
Consumer with DynamoDB Persistence - LocalStack Compatible

This script reads from Kinesis, detects anomalies, and writes them to DynamoDB.
Works with both LocalStack (local) and AWS (production).

Usage:
    # LocalStack mode
    USE_LOCALSTACK=true python consume_and_update_local.py
    
    # AWS production mode
    USE_LOCALSTACK=false python consume_and_update_local.py
"""

import time
import json
from decimal import Decimal
from localstack_config import get_kinesis_client, get_dynamodb_resource

# Anomaly detection thresholds
THRESHOLDS = {
    'HeartRate': {'min': 60, 'max': 100},
    'SPO2': {'min': 85, 'max': 110},
    'Temperature': {'min': 96, 'max': 101}
}


def detect_anomaly(readings):
    """
    Check if vital sign reading is anomalous.
    
    Args:
        readings (dict): Reading with 'datatype' and 'value' keys
    
    Returns:
        bool: True if anomaly detected, False otherwise
    """
    datatype = readings.get('datatype')
    value = readings.get('value')
    
    if datatype not in THRESHOLDS:
        return False
    
    # Handle both Decimal and numeric types
    if isinstance(value, Decimal):
        value = float(value)
    value = int(value)
    
    threshold = THRESHOLDS[datatype]
    return value < threshold['min'] or value > threshold['max']


def main():
    """Main execution function."""
    print("🏥 Bedside Monitor - Anomaly Detector with DynamoDB (LocalStack Compatible)")
    print("📊 Reading from stream: BSM_Stream")
    print("💾 Writing anomalies to table: BSM_anamoly")
    print("⏸️  Press Ctrl+C to stop\n")
    
    # Get AWS clients (auto-configured for LocalStack or AWS)
    kinesis_client = get_kinesis_client()
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('BSM_anamoly')
    
    # Get shard iterator
    shard_iterator = kinesis_client.get_shard_iterator(
        StreamName='BSM_Stream',
        ShardId='shardId-000000000000',
        ShardIteratorType='LATEST',
    )['ShardIterator']
    
    anomaly_count = 0
    record_count = 0
    
    try:
        while True:
            # Get records from stream
            response = kinesis_client.get_records(ShardIterator=shard_iterator)
            shard_iterator = response['NextShardIterator']
            
            if len(response['Records']) > 0:
                for item in response['Records']:
                    # Parse with Decimal for DynamoDB compatibility
                    readings = json.loads(item["Data"], parse_float=Decimal)
                    record_count += 1
                    
                    print(f"📥 Record #{record_count}: {readings}")
                    
                    # Check for anomaly
                    if detect_anomaly(readings):
                        anomaly_count += 1
                        
                        # Write to DynamoDB
                        try:
                            table.put_item(Item=readings)
                            print(f"🚨 Anomaly detected and saved to DynamoDB! (Total: {anomaly_count})")
                            print(f"   ⚠️  {readings['datatype']}: {readings['value']} "
                                  f"(Normal: {THRESHOLDS[readings['datatype']]['min']}-"
                                  f"{THRESHOLDS[readings['datatype']]['max']})")
                        except Exception as e:
                            print(f"   ❌ Error writing to DynamoDB: {e}")
                    else:
                        print(f"   ✅ Normal reading")
                    
                    print()
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Consumer stopped by user")
        print(f"📊 Statistics:")
        print(f"   Total records processed: {record_count}")
        print(f"   Anomalies detected and saved: {anomaly_count}")
        if record_count > 0:
            print(f"   Anomaly rate: {(anomaly_count/record_count)*100:.2f}%")
        
        # Query DynamoDB to verify
        print(f"\n💾 Verifying DynamoDB entries...")
        try:
            response = table.scan()
            print(f"   Total items in table: {response['Count']}")
        except Exception as e:
            print(f"   ❌ Error querying DynamoDB: {e}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == '__main__':
    main()
