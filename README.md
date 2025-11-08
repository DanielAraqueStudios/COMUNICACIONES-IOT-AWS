# Bedside Monitor IoT System

**A real-time medical telemetry system using AWS IoT Core, Kinesis Data Streams, and DynamoDB for patient vital signs monitoring and anomaly detection.**

[![AWS IoT](https://img.shields.io/badge/AWS-IoT%20Core-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/iot-core/)
[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Data Format](#-data-format)
- [Anomaly Detection](#-anomaly-detection)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This project simulates a **Bedside Patient Monitoring System** that collects vital signs (heart rate, SpO2, and temperature), publishes them to AWS IoT Core via MQTT, streams the data through AWS Kinesis, detects anomalies in real-time, and persists critical alerts to DynamoDB.

**Key Use Case:** Remote patient monitoring with real-time anomaly detection for early intervention in critical care scenarios.

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  Bedside Monitor    │
│  (Python Script)    │
│  - Heart Rate       │
│  - SpO2             │
│  - Temperature      │
└──────────┬──────────┘
           │ MQTT (TLS/WebSocket)
           ▼
┌─────────────────────┐
│   AWS IoT Core      │
│   - Message Broker  │
│   - IoT Rules       │
└──────────┬──────────┘
           │ IoT Rule Action
           ▼
┌─────────────────────┐
│  Kinesis Stream     │
│  - Real-time data   │
│  - Multiple shards  │
└──────────┬──────────┘
           │
           ├─────────────────┬──────────────────┐
           ▼                 ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Consumer #1  │  │ Consumer #2  │  │ Consumer #3  │
    │ (Print only) │  │ (Print only) │  │ (DynamoDB)   │
    └──────────────┘  └──────────────┘  └──────┬───────┘
                                               ▼
                                        ┌──────────────┐
                                        │  DynamoDB    │
                                        │ BSM_anamoly  │
                                        └──────────────┘
```

### Component Breakdown

| Component | Description | Technology |
|-----------|-------------|------------|
| **Data Publisher** | Simulates bedside monitor generating vital signs | `BedSideMonitor.py`, `local_consumer.py` |
| **Message Broker** | Receives and routes MQTT messages | AWS IoT Core |
| **Stream Processing** | Real-time data streaming | AWS Kinesis Data Streams |
| **Anomaly Detector** | Identifies out-of-range vital signs | Python consumers |
| **Alert Storage** | Persists anomaly records | Amazon DynamoDB |

---

## ✨ Features

- ✅ **Real-time telemetry** publishing using MQTT over TLS or WebSocket
- ✅ **Multiple vital signs** monitoring (Heart Rate, SpO2, Temperature)
- ✅ **Configurable publishing intervals** for each metric type
- ✅ **Secure authentication** via X.509 certificates or AWS credentials
- ✅ **Stream-based architecture** for scalability
- ✅ **Automatic anomaly detection** with configurable thresholds
- ✅ **Persistent anomaly logging** in DynamoDB
- ✅ **Connection resilience** with automatic reconnection and offline queuing

---

## 🔧 Prerequisites

### AWS Resources

You need the following AWS resources configured:

1. **AWS IoT Core**
   - IoT Thing created
   - X.509 certificates and private key downloaded
   - IoT Policy attached allowing `iot:Connect`, `iot:Publish`, `iot:Subscribe`
   - IoT Rule to forward messages to Kinesis

2. **Amazon Kinesis Data Streams**
   - Stream names used in the project:
     - `BSMStream` (used by `consumer_and_anomaly_detector.py`)
     - `BSM_Stream` (used by `consume_and_update.py`)
     - `BSM_Data_Stream1` (used by `local_consumer.py`)
   - At least 1 shard per stream

3. **Amazon DynamoDB**
   - Table name: `BSM_anamoly`
   - Primary key: `deviceid` (String)
   - Sort key: `timestamp` (String) - recommended

4. **AWS IAM Permissions**
   - `kinesis:GetRecords`, `kinesis:GetShardIterator`, `kinesis:DescribeStream`
   - `dynamodb:PutItem`, `dynamodb:GetItem`

### Local Environment

- **Python 3.7+**
- **pip** (Python package manager)
- **AWS CLI** configured with credentials (optional but recommended)

---

## 📦 Installation

### 1. Clone the Repository

```powershell
git clone https://github.com/DanielAraqueStudios/COMUNICACIONES-IOT-AWS.git
cd COMUNICACIONES-IOT-AWS
```

### 2. Install Python Dependencies

```powershell
pip install AWSIoTPythonSDK boto3
```

**Dependencies:**
- `AWSIoTPythonSDK` - AWS IoT Device SDK for MQTT communication
- `boto3` - AWS SDK for Python (Kinesis, DynamoDB)

### 3. Configure AWS Credentials

Set up your AWS credentials using one of these methods:

**Option A: AWS CLI**
```powershell
aws configure
```

**Option B: Environment Variables**
```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

**Option C: IAM Role** (if running on EC2/Lambda)

---

## ⚙️ Configuration

### IoT Certificates Setup

1. Download your IoT Thing certificates from AWS IoT Console
2. Place files in your project directory:
   - `root-CA.crt` - Amazon Root CA certificate
   - `device.cert.pem` - Device certificate
   - `device.private.key` - Private key

### Stream Names Configuration

⚠️ **Important:** The project uses different Kinesis stream names in different files. Verify your AWS stream names and update accordingly:

| File | Current Stream Name | Line to Update |
|------|---------------------|----------------|
| `consume_and_update.py` | `BSM_Stream` | Line 15 |
| `consumer_and_anomaly_detector.py` | `BSMStream` | Line 6 |
| `local_consumer.py` | `BSM_Data_Stream1` | Line 7 |

### DynamoDB Table Configuration

Verify the table name in `consume_and_update.py`:
```python
table = dynamodb.Table('BSM_anamoly')  # Line 11
```

---

## 🚀 Usage

### Publishing Vital Signs Data

#### Using BedSideMonitor.py (Recommended)

**Publish mode with X.509 certificates:**
```powershell
python BedSideMonitor.py `
  -e a1b2c3d4e5f6g7.iot.us-east-1.amazonaws.com `
  -r root-CA.crt `
  -c device.cert.pem `
  -k device.private.key `
  -id BSM_G101 `
  -t healthcare/monitors/BSM_G101 `
  -m publish
```

**Publish mode with WebSocket:**
```powershell
python BedSideMonitor.py `
  -e a1b2c3d4e5f6g7.iot.us-east-1.amazonaws.com `
  -r root-CA.crt `
  -w `
  -id BSM_G101 `
  -t healthcare/monitors/BSM_G101 `
  -m publish
```

**Both publish and subscribe:**
```powershell
python BedSideMonitor.py `
  -e a1b2c3d4e5f6g7.iot.us-east-1.amazonaws.com `
  -r root-CA.crt `
  -c device.cert.pem `
  -k device.private.key `
  -id BSM_G101 `
  -t healthcare/monitors/BSM_G101 `
  -m both
```

#### Using local_consumer.py (Alternative)

```powershell
python local_consumer.py `
  -e a1b2c3d4e5f6g7.iot.us-east-1.amazonaws.com `
  -r root-CA.crt `
  -c device.cert.pem `
  -k device.private.key `
  -m publish
```

### Consuming and Processing Data

#### Monitor Anomalies (Print Only)

```powershell
python consumer_and_anomaly_detector.py
```

**Output:**
```
{'deviceid': 'BSM_G101', 'timestamp': '2025-11-08 10:23:45.123456', 'datatype': 'HeartRate', 'value': 115}
Anomaly detected
```

#### Persist Anomalies to DynamoDB

```powershell
python consume_and_update.py
```

**Output:**
```
{'deviceid': 'BSM_G101', 'timestamp': '2025-11-08 10:23:45.123456', 'datatype': 'HeartRate', 'value': 115}
Anomaly detected, entry added in DynamoDB Table
```

---

## 📊 Data Format

### Published Message Schema

All messages published to AWS IoT Core follow this JSON schema:

```json
{
  "deviceid": "BSM_G101",
  "timestamp": "2025-11-08 10:23:45.123456",
  "datatype": "HeartRate",
  "value": 85
}
```

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `deviceid` | String | Unique device identifier | `BSM_G101` |
| `timestamp` | String | ISO-format timestamp | `2025-11-08 10:23:45.123456` |
| `datatype` | String | Type of vital sign | `HeartRate`, `SPO2`, `Temperature` |
| `value` | Number | Measured value | `85` (int or float) |

### Data Generation Parameters

| Metric | Distribution | Mean (μ) | Std Dev (σ) | Publish Interval | Format |
|--------|--------------|----------|-------------|------------------|--------|
| **Heart Rate** | Normal | 85 bpm | 12 bpm | Every 1 second | Integer |
| **SpO2** | Normal | 90% | 3% | Every 10 seconds | Integer |
| **Temperature** | Normal | 99°F | 1.5°F | Every 15 seconds | Float (1 decimal) |

---

## 🚨 Anomaly Detection

### Threshold Configuration

Anomalies are detected when vital signs fall outside the following ranges:

| Vital Sign | Normal Range | Anomaly Condition |
|------------|--------------|-------------------|
| **Heart Rate** | 60-100 bpm | `value < 60` OR `value > 100` |
| **SpO2** | 85-110% | `value < 85` OR `value > 110` |
| **Temperature** | 96-101°F | `value < 96` OR `value > 101` |

### Detection Logic Example

```python
# From consumer_and_anomaly_detector.py
if (readings['datatype'] == 'HeartRate') and ((60 > int(readings['value'])) or (int(readings['value']) > 100)):
    print("Anomaly detected")
```

### DynamoDB Anomaly Record

When an anomaly is detected, the entire reading is persisted:

```json
{
  "deviceid": "BSM_G101",
  "timestamp": "2025-11-08 10:23:45.123456",
  "datatype": "HeartRate",
  "value": 115
}
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Connection Refused / Certificate Error**

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**
- Verify IoT endpoint URL is correct
- Ensure certificate files are in the correct location
- Check that certificates are not expired
- Verify IoT Policy allows `iot:Connect`

#### 2. **ResourceNotFoundException: Stream Not Found**

**Symptoms:**
```
botocore.exceptions.ClientError: An error occurred (ResourceNotFoundException) when calling the GetShardIterator operation
```

**Solutions:**
- Verify Kinesis stream exists: `aws kinesis describe-stream --stream-name BSM_Stream`
- Update stream name in Python files to match your AWS resources
- Check AWS region matches in boto3 client and AWS credentials

#### 3. **No Data Appearing in Kinesis**

**Symptoms:**
- Publisher runs without errors
- Consumers receive no records

**Solutions:**
- Verify IoT Rule is configured to forward messages to Kinesis
- Check IoT Rule SQL statement: `SELECT * FROM 'your/topic/name'`
- Verify IoT Rule has permission to write to Kinesis (IAM role)
- Test with AWS IoT Core MQTT test client

#### 4. **DynamoDB Access Denied**

**Symptoms:**
```
botocore.exceptions.ClientError: An error occurred (AccessDeniedException)
```

**Solutions:**
- Verify IAM user/role has `dynamodb:PutItem` permission
- Check table name spelling: `BSM_anamoly` (note the typo in "anamoly")
- Verify table exists: `aws dynamodb describe-table --table-name BSM_anamoly`

#### 5. **Shard Iterator Expires**

**Symptoms:**
```
InvalidArgumentException: Shard iterator has expired
```

**Solutions:**
- This is normal for long-running consumers; the code automatically refreshes
- Reduce `time.sleep()` interval if you need faster processing
- Consider using Kinesis Client Library (KCL) for production

---

## 📁 Project Structure

```
COMUNICACIONES-IOT-AWS/
│
├── .github/
│   └── copilot-instructions.md    # AI agent guidance
│
├── BedSideMonitor.py              # Primary MQTT publisher with CLI args
├── local_consumer.py              # Alternative MQTT publisher
├── consumer_and_anomaly_detector.py   # Kinesis consumer (print only)
├── consume_and_update.py          # Kinesis consumer + DynamoDB writer
│
├── README.md                      # This file
├── requirements.txt               # Python dependencies (create this)
│
└── certificates/                  # (Create this directory)
    ├── root-CA.crt
    ├── device.cert.pem
    └── device.private.key
```

---

## 🔐 Security Best Practices

1. **Never commit certificates or keys** to version control
   - Add `*.pem`, `*.key`, `*.crt` to `.gitignore`

2. **Use IAM roles** when running on AWS infrastructure (EC2, Lambda)
   - Avoid hardcoding AWS credentials

3. **Rotate certificates** regularly
   - AWS IoT supports certificate rotation without downtime

4. **Restrict IoT Policy** to minimum required permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": ["iot:Connect", "iot:Publish"],
       "Resource": [
         "arn:aws:iot:us-east-1:123456789012:client/BSM_G101",
         "arn:aws:iot:us-east-1:123456789012:topic/healthcare/monitors/*"
       ]
     }]
   }
   ```

5. **Enable AWS CloudTrail** for audit logging

---

## 🧪 Testing

### Manual Testing

1. **Test MQTT Publishing:**
   - Subscribe to your topic in AWS IoT Core MQTT test client
   - Run `BedSideMonitor.py` in publish mode
   - Verify messages appear in test client

2. **Test Kinesis Streaming:**
   - Run a consumer script
   - Verify data appears in console output

3. **Test DynamoDB Persistence:**
   - Generate anomalous values (modify thresholds temporarily)
   - Check DynamoDB table for new items:
     ```powershell
     aws dynamodb scan --table-name BSM_anamoly
     ```

### Generating Test Anomalies

Temporarily modify `BedSideMonitor.py` to force anomalies:

```python
# Force high heart rate anomaly
value = 120  # Instead of random.normalvariate(85, 12)
```

---

## 📈 Performance Considerations

### Throughput

- **Single Publisher:** ~3 messages/second (1 HR + 0.1 SpO2 + 0.067 Temp)
- **Kinesis Shard:** Up to 1,000 records/second or 1 MB/second
- **DynamoDB:** On-demand pricing scales automatically

### Latency

- **MQTT → IoT Core:** < 50ms
- **IoT Core → Kinesis:** < 100ms
- **Kinesis → Consumer:** 200ms (due to polling interval)
- **Consumer → DynamoDB:** < 20ms

### Cost Optimization

- Use **Kinesis Data Firehose** for batch writing to reduce DynamoDB costs
- Implement **DynamoDB TTL** to automatically delete old anomaly records
- Use **IoT Core Basic Ingest** to reduce messaging costs (bypass IoT rules engine)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m "Add: real-time dashboard"`)
6. Push to your fork (`git push origin feature/improvement`)
7. Open a Pull Request

### Areas for Improvement

- [ ] Normalize Kinesis stream names into a single configuration file
- [ ] Add unit tests for anomaly detection logic
- [ ] Implement Kinesis Client Library (KCL) for production-grade consumers
- [ ] Add CloudWatch metrics and alarms
- [ ] Create Terraform/CloudFormation templates for infrastructure
- [ ] Build a real-time dashboard using Amazon QuickSight or Grafana
- [ ] Add support for multiple devices with unique IDs

---

## 📄 License

This project is licensed under the **Apache License 2.0**.

Original AWS IoT sample code © 2010-2017 Amazon.com, Inc. or its affiliates.  
Modified by GreatLearning.in for educational purposes.  
Further modifications by Daniel Araque Studios.

See [LICENSE](LICENSE) file for details.

---

## 📞 Support

For questions or issues:

- **GitHub Issues:** [Create an issue](https://github.com/DanielAraqueStudios/COMUNICACIONES-IOT-AWS/issues)
- **AWS Documentation:** [AWS IoT Core](https://docs.aws.amazon.com/iot/)
- **Email:** Contact repository owner

---

## 🙏 Acknowledgments

- **AWS IoT Team** for the Python SDK and sample code
- **GreatLearning.in** for educational modifications
- **Universidad Militar Nueva Granada** - Mechatronics Engineering Program

---

<div align="center">
  
**Built with ❤️ for healthcare IoT applications**

</div>
