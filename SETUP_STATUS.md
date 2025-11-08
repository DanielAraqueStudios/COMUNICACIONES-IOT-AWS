# LocalStack Quick Setup Instructions

## Current Status ✅
- ✅ Python 3.13.2 installed
- ✅ LocalStack auth token configured
- ✅ AWS credentials set (test mode)
- ✅ Environment file (.env) created
- ❌ Docker not running
- ⏳ Python dependencies need installation

---

## Step 1: Start Docker Desktop ⚠️

**You need to start Docker Desktop first!**

1. Open **Docker Desktop** application
2. Wait for it to fully start (status should show "Docker Desktop is running")
3. Verify with: `docker ps` (should not show error)

---

## Step 2: Install Python Dependencies

Once your pip issue is resolved, run ONE of these commands:

### Option A: Using requirements.txt (Recommended)
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Option B: Install packages individually
```powershell
python -m pip install --upgrade pip
python -m pip install AWSIoTPythonSDK
python -m pip install boto3
python -m pip install localstack
python -m pip install awscli-local
python -m pip install docker
python -m pip install python-dotenv
python -m pip install requests
```

### Option C: If pip has issues, try reinstalling Python or:
```powershell
# Download get-pip.py
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "get-pip.py"
python get-pip.py
```

---

## Step 3: Start LocalStack

### Option A: Using Docker Compose (Automated)
```powershell
# Start LocalStack
docker-compose up -d

# Wait 30 seconds for initialization
Start-Sleep -Seconds 30

# Check status
docker ps
docker-compose logs localstack
```

### Option B: Using LocalStack CLI (Alternative)
```powershell
# Start LocalStack
localstack start -d

# Wait for ready
localstack wait -t 30
```

---

## Step 4: Verify Setup

```powershell
# Test LocalStack is responding
Invoke-WebRequest -Uri "http://localhost:4566/_localstack/health" -UseBasicParsing

# List Kinesis streams (should show 3 streams after init)
awslocal kinesis list-streams

# List DynamoDB tables (should show BSM_anamoly)
awslocal dynamodb list-tables
```

---

## Step 5: Test Configuration

```powershell
# Run the configuration test
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

## Step 6: Run the System

### Terminal 1: Start Publisher
```powershell
# Publish data to Kinesis
python kinesis_publisher_local.py
```

### Terminal 2: Start Consumer (Print Only)
```powershell
# Set environment
$env:USE_LOCALSTACK="true"

# Run consumer
python consumer_and_anomaly_detector_local.py
```

### Terminal 3: Start DynamoDB Writer
```powershell
# Set environment
$env:USE_LOCALSTACK="true"

# Run consumer with DB writes
python consume_and_update_local.py
```

---

## Troubleshooting

### Issue: "pip is not recognized"
**Solution:** 
- Ensure Python is in PATH
- Use `python -m pip` instead of `pip`
- Reinstall Python with "Add to PATH" checked

### Issue: "Docker is not running"
**Solution:**
- Start Docker Desktop application
- Wait for it to fully initialize
- Check system tray for Docker icon (should be green)

### Issue: "awslocal: command not found"
**Solution:**
```powershell
# Install awscli-local
python -m pip install awscli-local

# Alternative: use aws with endpoint
aws --endpoint-url=http://localhost:4566 kinesis list-streams
```

### Issue: "Cannot connect to LocalStack"
**Solution:**
1. Check Docker is running: `docker ps`
2. Check LocalStack logs: `docker-compose logs localstack`
3. Restart LocalStack: `docker-compose restart localstack`
4. Check firewall isn't blocking port 4566

### Issue: Streams/Tables not created
**Solution:**
```powershell
# Manually create resources
awslocal kinesis create-stream --stream-name BSMStream --shard-count 1
awslocal kinesis create-stream --stream-name BSM_Stream --shard-count 1
awslocal kinesis create-stream --stream-name BSM_Data_Stream1 --shard-count 1

awslocal dynamodb create-table `
  --table-name BSM_anamoly `
  --attribute-definitions AttributeName=deviceid,AttributeType=S AttributeName=timestamp,AttributeType=S `
  --key-schema AttributeName=deviceid,KeyType=HASH AttributeName=timestamp,KeyType=RANGE `
  --billing-mode PAY_PER_REQUEST
```

---

## Quick Commands Reference

```powershell
# Start LocalStack
docker-compose up -d

# Stop LocalStack
docker-compose down

# View logs
docker-compose logs -f localstack

# Check health
Invoke-WebRequest http://localhost:4566/_localstack/health

# List resources
awslocal kinesis list-streams
awslocal dynamodb list-tables

# Query anomalies
awslocal dynamodb scan --table-name BSM_anamoly
```

---

## What to Do Right Now

1. ✅ **Start Docker Desktop** - This is REQUIRED
2. ⏳ **Fix pip/Python** - Reinstall or upgrade pip
3. 📦 **Install dependencies** - Run `python -m pip install -r requirements.txt`
4. 🚀 **Start LocalStack** - Run `docker-compose up -d`
5. 🧪 **Test it** - Run `python localstack_config.py`
6. 🎯 **Run the system** - Start publisher and consumers

---

## Need Help?

Check these files:
- `LOCALSTACK_SETUP.md` - Complete detailed guide
- `README.md` - Project overview
- `.env` - Your environment configuration

Run automated setup (after fixing pip and starting Docker):
```powershell
.\setup_localstack.ps1
```
