# LocalStack Setup Guide

**Run the complete Bedside Monitor IoT System locally using LocalStack**

This guide explains how to set up and run the entire AWS infrastructure locally on your machine using LocalStack, eliminating the need for AWS cloud resources during development.

---

## 📋 Table of Contents

- [What is LocalStack?](#what-is-localstack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Running the System](#running-the-system)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Switching Between LocalStack and AWS](#switching-between-localstack-and-aws)

---

## 🎯 What is LocalStack?

**LocalStack** is a fully functional local AWS cloud stack that allows you to develop and test cloud applications offline. It provides:

- ✅ **Kinesis Data Streams** for real-time data streaming
- ✅ **DynamoDB** for NoSQL database operations
- ✅ **CloudWatch Logs** for monitoring
- ✅ **And 80+ other AWS services**

**Benefits:**
- 💰 Zero AWS costs during development
- ⚡ Faster iteration (no network latency)
- 🔒 Complete data privacy (everything stays local)
- 🧪 Safe experimentation (no production impact)

---

## 🔧 Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop
   - Ensure Docker is running before proceeding

2. **Python 3.7+**
   ```powershell
   python --version
   ```

3. **pip** (Python package manager)
   ```powershell
   pip --version
   ```

### System Requirements

- **RAM:** Minimum 4GB, recommended 8GB+
- **Disk Space:** 5GB free
- **Network:** Internet connection for initial setup

---

## 📦 Installation

### Step 1: Install Python Dependencies

```powershell
# Navigate to project directory
cd "C:\Users\danie\OneDrive - unimilitar.edu.co\Documentos\UNIVERSIDADDDDDDDDDDDDDDDDDDDDDDDDDD\MECATRÓNICA\SEXTO SEMESTRE\COMUNICACIONES\COMUNICACIONES-IOT-AWS"

# Install all dependencies including LocalStack
pip install -r requirements.txt
```

This installs:
- `localstack` - LocalStack core
- `awscli-local` - AWS CLI wrapper for LocalStack
- `boto3` - AWS SDK for Python
- `AWSIoTPythonSDK` - IoT MQTT client
- Other dependencies

### Step 2: Verify Docker Installation

```powershell
docker --version
docker ps
```

Expected output:
```
Docker version 24.0.0, build ...
CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES
```

### Step 3: Configure Environment

Copy the example environment file:

```powershell
# PowerShell
Copy-Item .env.example .env
```

Edit `.env` and ensure these settings:

```ini
USE_LOCALSTACK=true
LOCALSTACK_ENDPOINT=http://localhost:4566
AWS_DEFAULT_REGION=us-east-1
```

---

## 🚀 Quick Start

### Option A: Using Docker Compose (Recommended)

```powershell
# Start LocalStack with all services
docker-compose up -d

# Wait for initialization (about 30 seconds)
Start-Sleep -Seconds 30

# Verify services are running
awslocal kinesis list-streams
awslocal dynamodb list-tables
```

### Option B: Using LocalStack CLI

```powershell
# Start LocalStack
localstack start -d

# Wait for services
Start-Sleep -Seconds 30

# Run initialization script
bash localstack_init/init.sh
```

---

## 🔨 Detailed Setup

### 1. Start LocalStack

```powershell
# Using Docker Compose (recommended)
docker-compose up -d

# Check logs
docker-compose logs -f localstack
```

You should see:
```
bedside-monitor-localstack | Ready.
```

### 2. Create AWS Resources

The `localstack_init/init.sh` script automatically creates:

#### Kinesis Streams:
- `BSMStream` (1 shard)
- `BSM_Stream` (1 shard)
- `BSM_Data_Stream1` (1 shard)

#### DynamoDB Table:
- `BSM_anamoly` (deviceid + timestamp keys)

**Verify creation:**

```powershell
# List Kinesis streams
awslocal kinesis list-streams

# Describe DynamoDB table
awslocal dynamodb describe-table --table-name BSM_anamoly
```

### 3. Test Configuration

Run the configuration test:

```powershell
python localstack_config.py
```

Expected output:
```
🧪 Testing LocalStack Configuration

1️⃣ Testing Kinesis client...
🔧 Using LocalStack endpoint: http://localhost:4566
   Available streams: ['BSMStream', 'BSM_Stream', 'BSM_Data_Stream1']

2️⃣ Testing DynamoDB resource...
   Available tables: ['BSM_anamoly']

3️⃣ Testing Kinesis put_record...
✅ Published to BSM_Stream: {...}

✅ Configuration test complete!
```

---

## 🏃 Running the System

### Complete Workflow

#### Terminal 1: Start LocalStack
```powershell
docker-compose up
```

#### Terminal 2: Start Publisher
```powershell
# Set environment for LocalStack
$env:USE_LOCALSTACK="true"

# Run Kinesis publisher (bypasses IoT Core)
python kinesis_publisher_local.py --stream BSM_Stream --device-id BSM_G101
```

Expected output:
```
🏥 Bedside Monitor Kinesis Publisher
📊 Publishing to stream: BSM_Stream
🔖 Device ID: BSM_G101
⏸️  Press Ctrl+C to stop

🔧 Using LocalStack endpoint: http://localhost:4566
✅ Published to BSM_Stream: {"deviceid": "BSM_G101", "timestamp": "2025-11-08...", "datatype": "HeartRate", "value": 85}
```

#### Terminal 3: Run Anomaly Detector (Print Only)
```powershell
# Set environment
$env:USE_LOCALSTACK="true"

# Run consumer
python consumer_and_anomaly_detector.py
```

Expected output:
```
🔧 Using LocalStack endpoint: http://localhost:4566
{'deviceid': 'BSM_G101', 'timestamp': '2025-11-08...', 'datatype': 'HeartRate', 'value': 115}
Anomaly detected
```

#### Terminal 4: Run DynamoDB Writer
```powershell
# Set environment
$env:USE_LOCALSTACK="true"

# Run consumer with DB writes
python consume_and_update.py
```

Expected output:
```
🔧 Using LocalStack endpoint: http://localhost:4566
{'deviceid': 'BSM_G101', 'timestamp': '2025-11-08...', 'datatype': 'HeartRate', 'value': 115}
Anomaly detected, entry added in DynamoDB Table
```

---

## ✅ Verification

### 1. Check Kinesis Stream Data

```powershell
# Get shard iterator
awslocal kinesis get-shard-iterator `
  --stream-name BSM_Stream `
  --shard-id shardId-000000000000 `
  --shard-iterator-type LATEST

# Get records (use the iterator from above)
awslocal kinesis get-records `
  --shard-iterator "AAA..."
```

### 2. Query DynamoDB for Anomalies

```powershell
# Scan table for all anomalies
awslocal dynamodb scan --table-name BSM_anamoly

# Get specific device anomalies
awslocal dynamodb query `
  --table-name BSM_anamoly `
  --key-condition-expression "deviceid = :did" `
  --expression-attribute-values '{":did":{"S":"BSM_G101"}}'
```

### 3. Monitor with AWS CLI Local

```powershell
# Check stream status
awslocal kinesis describe-stream --stream-name BSM_Stream

# Count table items
awslocal dynamodb describe-table --table-name BSM_anamoly | Select-String "ItemCount"
```

---

## 🛠️ Troubleshooting

### Issue 1: LocalStack Won't Start

**Symptoms:**
```
Error response from daemon: driver failed programming external connectivity
```

**Solutions:**
1. Check if port 4566 is already in use:
   ```powershell
   netstat -ano | findstr :4566
   ```
2. Stop conflicting process or change port in `docker-compose.yml`
3. Restart Docker Desktop

### Issue 2: Python Can't Connect to LocalStack

**Symptoms:**
```
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL
```

**Solutions:**
1. Verify LocalStack is running:
   ```powershell
   docker ps | findstr localstack
   ```
2. Check endpoint URL:
   ```powershell
   curl http://localhost:4566/_localstack/health
   ```
3. Ensure `USE_LOCALSTACK=true` in environment

### Issue 3: Streams/Tables Not Found

**Symptoms:**
```
ResourceNotFoundException: Stream BSM_Stream not found
```

**Solutions:**
1. Re-run initialization:
   ```powershell
   docker-compose restart localstack
   # Wait 30 seconds for init script
   ```
2. Manually create resources:
   ```powershell
   awslocal kinesis create-stream --stream-name BSM_Stream --shard-count 1
   ```

### Issue 4: No Data in Kinesis

**Symptoms:**
- Publisher runs without errors
- Consumer receives no records

**Solutions:**
1. Verify stream name matches in publisher and consumer
2. Check data using AWS CLI:
   ```powershell
   awslocal kinesis describe-stream --stream-name BSM_Stream
   ```
3. Increase consumer polling interval or reduce `time.sleep()`

### Issue 5: Permission Denied on init.sh

**Symptoms:**
```
Permission denied: init.sh
```

**Solutions (Git Bash or WSL):**
```bash
chmod +x localstack_init/init.sh
```

---

## 🔄 Switching Between LocalStack and AWS

### Using LocalStack (Development)

```powershell
# Set environment variable
$env:USE_LOCALSTACK="true"

# Run scripts
python kinesis_publisher_local.py
python consume_and_update.py
```

### Using AWS Production

```powershell
# Set environment variable
$env:USE_LOCALSTACK="false"

# Configure AWS credentials
aws configure

# Run scripts with AWS endpoints
python BedSideMonitor.py -e <iot-endpoint> -r root-CA.crt -c cert.pem -k key.pem -m publish
python consume_and_update.py
```

### Environment File Method

Edit `.env`:

```ini
# For LocalStack
USE_LOCALSTACK=true

# For AWS Production
# USE_LOCALSTACK=false
```

Then use `python-dotenv` to load automatically:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 📊 LocalStack Dashboard (Optional)

LocalStack Pro includes a web dashboard. For the free version, use CLI commands:

```powershell
# View all resources
awslocal resourcegroupstaggingapi get-resources

# Monitor logs
docker-compose logs -f localstack
```

---

## 🧹 Cleanup

### Stop LocalStack

```powershell
# Stop containers
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v
```

### Remove Python Virtual Environment

```powershell
deactivate  # If in virtual environment
Remove-Item -Recurse -Force venv
```

---

## 📈 Performance Tips

1. **Increase Docker Memory:** Docker Desktop → Settings → Resources → Memory (4GB+)
2. **Use Persistence:** Keep `PERSISTENCE=1` in docker-compose.yml to avoid recreating resources
3. **Reduce Latency:** Set `KINESIS_LATENCY=0` for faster local testing
4. **Disable Debug:** Set `DEBUG=0` for better performance

---

## 🔗 Useful Commands Reference

### Docker Commands
```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps
```

### AWS Local Commands
```powershell
# Kinesis
awslocal kinesis list-streams
awslocal kinesis describe-stream --stream-name BSM_Stream

# DynamoDB
awslocal dynamodb list-tables
awslocal dynamodb scan --table-name BSM_anamoly

# General
awslocal --endpoint-url=http://localhost:4566 <service> <command>
```

---

## 📚 Additional Resources

- **LocalStack Documentation:** https://docs.localstack.cloud/
- **AWS CLI Local:** https://github.com/localstack/awscli-local
- **LocalStack GitHub:** https://github.com/localstack/localstack
- **Docker Documentation:** https://docs.docker.com/

---

## 🤝 Support

If you encounter issues:

1. Check LocalStack logs: `docker-compose logs localstack`
2. Verify Docker is running: `docker ps`
3. Test connectivity: `curl http://localhost:4566/_localstack/health`
4. Consult troubleshooting section above
5. Open an issue on GitHub

---

**🎉 You're now ready to develop locally with LocalStack!**

No AWS account or internet connection needed for development and testing.
