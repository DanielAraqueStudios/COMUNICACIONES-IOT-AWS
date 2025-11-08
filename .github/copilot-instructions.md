## Repo snapshot

- Top-level scripts: `BedSideMonitor.py`, `local_consumer.py`, `consume_and_update.py`, `consumer_and_anomaly_detector.py`.
- Purpose: simulate/publish bedside-monitor readings to AWS IoT/Kinesis and consume them to detect anomalies and persist to DynamoDB.

## Big picture (what this project does)

- Device publisher: `BedSideMonitor.py` / `local_consumer.py` use AWS IoT MQTT (AWSIoTPythonSDK) to publish JSON readings with keys: `deviceid`, `timestamp`, `datatype`, `value`.
- Streaming: other scripts read from Kinesis streams (several different stream names appear in code — see notes below) and either print anomalies or write anomaly records to DynamoDB.

## Key files & patterns (quick references)

- `BedSideMonitor.py` — MQTT publisher using `AWSIoTPythonSDK.MQTTLib`; CLI args required: `-e/--endpoint`, `-r/--rootCA`, `-c/--cert`, `-k/--key`, `-t/--topic`, `-m/--mode`. Example payload created in `publishBedSideMonitorData()`.
- `local_consumer.py` — another MQTT example (derived from AWS sample). Uses `customCallback()` and publishes simulated Temperature/HeartRate/SPO2 values on a scheduler.
- `consumer_and_anomaly_detector.py` — reads from Kinesis Stream `BSMStream` and prints anomalies (no DB writes).
- `consume_and_update.py` — reads from Kinesis Stream `BSM_Stream` and writes anomalies to DynamoDB table `BSM_anamoly` (note spelling).

## Concrete data formats & invariants

- Published JSON example: {"deviceid": "BSM_G101", "timestamp": "<iso>", "datatype": "HeartRate|SPO2|Temperature", "value": <number>}.
- Anomaly detection thresholds are hard-coded in consumers: HeartRate outside 60–100, SPO2 outside 85–110, Temperature outside 96–101.

## Important integration points & environment

- AWS SDK: boto3 (Kinesis, DynamoDB) — scripts expect valid AWS credentials in environment or instance profile.
- AWS IoT: `AWSIoTPythonSDK` client is used for MQTT; when running publishers you must supply either X.509 cert/key (`-c`/`-k`) or enable websocket mode and root CA accordingly.
- DynamoDB table name: `BSM_anamoly` (do not rename without confirming). Kinesis stream names vary across files (`BSMStream`, `BSM_Stream`, `BSM_Data_Stream1`) — confirm canonical name in AWS account before changing code.

## Developer workflows / run guidance

- To run the MQTT publisher: provide endpoint and certs. Example:

  ```powershell
  python BedSideMonitor.py -e <your-iot-endpoint> -r root-CA.crt -c cert.pem -k private.key -id BSM_G101 -t sdk/test/Python -m publish
  ```

- To run a Kinesis consumer locally (reads indefinitely):

  ```powershell
  python consumer_and_anomaly_detector.py
  python consume_and_update.py  # writes anomalies to DynamoDB
  ```

## Project-specific conventions & gotchas for AI agents

- Leave external resource identifiers (stream names, table names, IoT endpoint, certificate file names) intact unless you verify the AWS environment — they differ between files.
- Scripts are procedural single-file scripts (no packaging). Prefer small, localized edits and preserve CLI argument shapes when present.
- Polling pattern: consumers call `get_shard_iterator(..., ShardIteratorType='LATEST')` and then loop with `get_records()` and `time.sleep(0.2)`. If you change polling or iterator behavior, test on a real stream to avoid data loss.
- DynamoDB write: `consume_and_update.py` calls `table.put_item(Item=readings)` using `readings` parsed via Decimal in JSON; preserve numeric type handling when modifying.

## Useful examples to copy/paste

- Publishing JSON (from `local_consumer.py`):

  ```python
  message = { 'deviceid':'BSM_G101','timestamp':str(datetime.datetime.now()),'datatype':'Temperature','value':value }
  myAWSIoTMQTTClient.publish(topic, json.dumps(message), 1)
  ```

- Kinesis read loop (from `consumer_and_anomaly_detector.py`):

  ```python
  response = client.get_records(ShardIterator=shardIterator)
  shardIterator = response['NextShardIterator']
  for item in response['Records']:
      readings = json.loads(item['Data'])
  ```

## When to ask the repo owner

- Confirm the canonical Kinesis stream name and the intended DynamoDB table name (the code uses multiple variants).
- Confirm whether MQTT clients should use websockets or X.509 certs for local testing.

## What I won't change automatically

- Hard-coded resource names (Kinesis stream names, DynamoDB table, IoT endpoint URLs, cert filenames), threshold values for anomaly detection — these are environment or domain decisions.

---
If you'd like, I can (1) normalize and centralize the stream/table names behind a config, (2) extract shared logic into a small package for easier testing, or (3) add a README with run/playbook steps. Which should I do next? 
