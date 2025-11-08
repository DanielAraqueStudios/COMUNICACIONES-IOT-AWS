"""
Local Kinesis Publisher - LocalStack Compatible

This script publishes simulated bedside monitor data directly to Kinesis
streams, bypassing AWS IoT Core. Perfect for local development with LocalStack.

Usage:
    # Using default LocalStack endpoint
    python kinesis_publisher_local.py
    
    # Using custom configuration
    USE_LOCALSTACK=true python kinesis_publisher_local.py
"""

import json
import time
import random
import datetime
import argparse
from localstack_config import put_kinesis_record


def generate_vital_signs(device_id='BSM_G101'):
    """
    Generate simulated vital signs data.
    
    Args:
        device_id (str): Device identifier
    
    Yields:
        dict: Vital sign reading with deviceid, timestamp, datatype, value
    """
    loop_count = 0
    
    while True:
        timestamp = str(datetime.datetime.now())
        
        # Publish heart rate every second
        if loop_count % 1 == 0:
            yield {
                'deviceid': device_id,
                'timestamp': timestamp,
                'datatype': 'HeartRate',
                'value': int(random.normalvariate(85, 12))
            }
        
        # Publish SpO2 every 10 seconds
        if loop_count % 10 == 0:
            yield {
                'deviceid': device_id,
                'timestamp': timestamp,
                'datatype': 'SPO2',
                'value': int(random.normalvariate(90, 3))
            }
        
        # Publish temperature every 15 seconds
        if loop_count % 15 == 0:
            yield {
                'deviceid': device_id,
                'timestamp': timestamp,
                'datatype': 'Temperature',
                'value': round(float(random.normalvariate(99, 1.5)), 1)
            }
        
        loop_count += 1
        time.sleep(1)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Publish bedside monitor data directly to Kinesis (LocalStack compatible)'
    )
    parser.add_argument(
        '-s', '--stream',
        default='BSM_Stream',
        help='Kinesis stream name (default: BSM_Stream)'
    )
    parser.add_argument(
        '-d', '--device-id',
        default='BSM_G101',
        help='Device identifier (default: BSM_G101)'
    )
    
    args = parser.parse_args()
    
    print(f"🏥 Bedside Monitor Kinesis Publisher")
    print(f"📊 Publishing to stream: {args.stream}")
    print(f"🔖 Device ID: {args.device_id}")
    print(f"⏸️  Press Ctrl+C to stop\n")
    
    try:
        for reading in generate_vital_signs(args.device_id):
            # Publish to Kinesis
            put_kinesis_record(
                stream_name=args.stream,
                data=json.dumps(reading),
                partition_key=args.device_id
            )
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Publisher stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == '__main__':
    main()
