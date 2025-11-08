#!/bin/bash

# LocalStack Initialization Script
# This script runs automatically when LocalStack starts
# It creates all necessary AWS resources locally

echo "🚀 Initializing LocalStack resources for Bedside Monitor..."

# Set AWS endpoint to LocalStack
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Wait for LocalStack to be ready
echo "⏳ Waiting for LocalStack to be ready..."
until awslocal kinesis list-streams > /dev/null 2>&1; do
  sleep 2
done
echo "✅ LocalStack is ready!"

# ============================================================================
# CREATE KINESIS STREAMS
# ============================================================================
echo "📊 Creating Kinesis Data Streams..."

# Create BSMStream (used by consumer_and_anomaly_detector.py)
awslocal kinesis create-stream \
  --stream-name BSMStream \
  --shard-count 1 \
  && echo "✅ Created stream: BSMStream" \
  || echo "⚠️  Stream BSMStream already exists"

# Create BSM_Stream (used by consume_and_update.py)
awslocal kinesis create-stream \
  --stream-name BSM_Stream \
  --shard-count 1 \
  && echo "✅ Created stream: BSM_Stream" \
  || echo "⚠️  Stream BSM_Stream already exists"

# Create BSM_Data_Stream1 (used by local_consumer.py)
awslocal kinesis create-stream \
  --stream-name BSM_Data_Stream1 \
  --shard-count 1 \
  && echo "✅ Created stream: BSM_Data_Stream1" \
  || echo "⚠️  Stream BSM_Data_Stream1 already exists"

# Wait for streams to become active
echo "⏳ Waiting for streams to become active..."
sleep 5

# ============================================================================
# CREATE DYNAMODB TABLE
# ============================================================================
echo "💾 Creating DynamoDB Table..."

awslocal dynamodb create-table \
  --table-name BSM_anamoly \
  --attribute-definitions \
    AttributeName=deviceid,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=deviceid,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  && echo "✅ Created table: BSM_anamoly" \
  || echo "⚠️  Table BSM_anamoly already exists"

# ============================================================================
# VERIFY RESOURCES
# ============================================================================
echo ""
echo "🔍 Verifying created resources..."
echo ""

echo "📊 Kinesis Streams:"
awslocal kinesis list-streams --output table

echo ""
echo "💾 DynamoDB Tables:"
awslocal dynamodb list-tables --output table

echo ""
echo "✅ LocalStack initialization complete!"
echo "🌐 LocalStack is running at: http://localhost:4566"
echo "📝 Use 'awslocal' instead of 'aws' for all CLI commands"
