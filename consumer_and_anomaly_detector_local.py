"""
Consumer with Anomaly Detection - LocalStack Compatible

This script reads from Kinesis Data Streams and detects vital sign anomalies.
Works with both LocalStack (local) and AWS (production).

Usage:
    # LocalStack mode
    USE_LOCALSTACK=true python consumer_and_anomaly_detector_local.py
    
    # AWS production mode
    USE_LOCALSTACK=false python consumer_and_anomaly_detector_local.py
"""

import time
import json
from localstack_config import get_kinesis_client

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
    value = int(readings.get('value', 0))
    
    if datatype not in THRESHOLDS:
        return False
    
    threshold = THRESHOLDS[datatype]
    return value < threshold['min'] or value > threshold['max']


def main():
    """Main execution function."""
    print("🏥 Bedside Monitor - Anomaly Detector (LocalStack Compatible)")
    print("📊 Reading from stream: BSMStream")
    print("⏸️  Press Ctrl+C to stop\n")
    
    # Get Kinesis client (auto-configured for LocalStack or AWS)
    client = get_kinesis_client()
    
    # Get shard iterator
    shard_iterator = client.get_shard_iterator(
        StreamName='BSMStream',
        ShardId='shardId-000000000000',
        ShardIteratorType='LATEST',
    )['ShardIterator']
    
    anomaly_count = 0
    record_count = 0
    
    try:
        while True:
            # Get records from stream
            response = client.get_records(ShardIterator=shard_iterator)
            shard_iterator = response['NextShardIterator']
            
            if len(response['Records']) > 0:
                for item in response['Records']:
                    readings = json.loads(item["Data"])
                    record_count += 1
                    
                    print(f"📥 Record #{record_count}: {readings}")
                    
                    # Check for anomaly
                    if detect_anomaly(readings):
                        anomaly_count += 1
                        print(f"🚨 Anomaly detected! (Total: {anomaly_count})")
                        print(f"   ⚠️  {readings['datatype']}: {readings['value']} "
                              f"(Normal: {THRESHOLDS[readings['datatype']]['min']}-"
                              f"{THRESHOLDS[readings['datatype']]['max']})")
                    else:
                        print(f"   ✅ Normal reading")
                    
                    print()
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Consumer stopped by user")
        print(f"📊 Statistics:")
        print(f"   Total records processed: {record_count}")
        print(f"   Anomalies detected: {anomaly_count}")
        if record_count > 0:
            print(f"   Anomaly rate: {(anomaly_count/record_count)*100:.2f}%")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == '__main__':
    main()
