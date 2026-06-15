# Real-Time Serverless Paper Trading Pipeline with Embedded AI Alerting

A high-throughput, event-driven data pipeline built on AWS that ingests simulated financial market ticks, runs real-time statistical anomaly detection, and streams live data to a globally accessible web dashboard—all engineered to run entirely within the **AWS Free Tier ($0.00/mo)**.

---

## 🚀 System Architecture

```text
[Local Python Producer]
       │ (High-Frequency JSON Ticks)
       ▼
  [Amazon SQS] (Decoupling & Buffer Queue)
       │ (Batch Trigger)
       ▼
  [AWS Lambda: Data Processor] ──(Inference)──► [Embedded Z-Score ML Model]
       │                                                 │
       ├─(If Anomaly: Trigger Alert)                     │ (Flag: True/False)
       │                                                 ▼
       ├─► [Amazon SES] ──► (Inbox Email Notification)   │
       │                                                 ▼
       └─► [Amazon DynamoDB] ◄───────────────────────────┘
               ▲
               │ (Scan/Query)
          [AWS Lambda: Reader API]
               ▲
               │ (HTTP GET /stocks)
          [Amazon API Gateway]
               ▲
               │ (Fetch Request)
          [Amazon S3 Static Website] ──► (User Browser Live Interface)
```

---

## 🛠️ Tech Stack & AWS Services

| Layer | Technology |
|---------|-----------|
| Data Generation | Python 3.12, boto3, json |
| Message Queue | Amazon SQS |
| Compute | AWS Lambda |
| Machine Learning | Embedded Z-Score Anomaly Detection |
| Database | Amazon DynamoDB |
| API Layer | Amazon API Gateway |
| Frontend Hosting | Amazon S3 Static Website |
| Notifications | Amazon SES |

---

## 💡 Key Engineering & Architectural Highlights

### 1. Decoupled Event-Driven Architecture

Instead of writing directly from the producer to the database, the system uses Amazon SQS as an intermediate message broker. This provides:

- Loose coupling between services
- Improved fault tolerance
- Burst traffic handling
- Guaranteed message durability
- Independent scaling of producer and consumer components

### 2. Cost-Optimized AI Inference

Rather than deploying a dedicated machine learning endpoint, anomaly detection is performed directly inside AWS Lambda using a lightweight statistical Z-Score model.

The detector is initialized outside the Lambda handler, enabling:

- Cold-start reuse
- Reduced execution latency
- Lower memory overhead
- Zero additional infrastructure costs

### 3. Real-Time Alerting Engine

When abnormal price movement is detected:

1. Lambda flags the event.
2. An alert record is stored in DynamoDB.
3. Amazon SES sends an email notification.
4. The dashboard reflects the anomaly in near real time.

### 4. Secure Cross-Origin Communication

The Reader API injects CORS headers:

```http
Access-Control-Allow-Origin: *
```

This allows the frontend hosted on Amazon S3 to safely communicate with the API Gateway endpoint.

### 5. Fully Serverless Design

The entire system is built using managed AWS services:

- No EC2 instances
- No container orchestration
- No infrastructure maintenance
- Automatic scaling
- Pay-per-use pricing

---

## 📂 Repository Structure

```text
.
├── producer/
│   └── free_producer.py
│
├── lambda_writer/
│   └── lambda_function.py
│
├── lambda_reader/
│   └── lambda_function.py
│
├── frontend/
│   └── index.htm;
│
├── images/
│   └── architecture.png
│
└── README.md
```

### Component Description

| Component | Purpose |
|------------|----------|
| producer | Generates simulated stock market data |
| lambda_writer | Processes queue messages and performs anomaly detection |
| lambda_reader | Provides REST API access to stored data |
| frontend | Displays live trading dashboard |
| images | Architecture diagrams and screenshots |

---

## 📋 Sample Pipeline Payloads

### Incoming SQS Message

```json
{
  "ticker": "TSLA",
  "price": 178.45,
  "volume": 945,
  "timestamp": "2026-06-15T10:46:21Z"
}
```

### Processed DynamoDB Record

```json
{
  "ticker": "TSLA",
  "timestamp": "2026-06-15T10:46:21Z",
  "price": 178.45,
  "volume": 945,
  "is_anomaly": true
}
```

### API Response

```json
[
  {
    "ticker": "TSLA",
    "timestamp": "2026-06-15T10:46:21Z",
    "price": 178.45,
    "volume": 945,
    "is_anomaly": true
  }
]
```

---

## 🔄 End-to-End Workflow

### Step 1: Market Data Generation

A local Python producer continuously generates simulated stock market ticks.

```python
{
  "ticker": "AAPL",
  "price": 215.12,
  "volume": 1023
}
```

### Step 2: Queue Ingestion

The producer pushes events into Amazon SQS.

Benefits:

- Reliable delivery
- Back-pressure handling
- Decoupled architecture

### Step 3: Lambda Processing

SQS triggers the Writer Lambda.

Responsibilities:

- Parse incoming messages
- Run anomaly detection
- Store records
- Trigger notifications

### Step 4: AI-Based Anomaly Detection

A Z-Score algorithm evaluates incoming stock prices.

```text
Z = (Current Price - Mean Price) / Standard Deviation
```

If:

```text
|Z| > Threshold
```

the event is classified as an anomaly.

### Step 5: Data Persistence

Processed records are stored in DynamoDB.

### Step 6: Alert Notification

Abnormal events trigger an email through Amazon SES.

### Step 7: Dashboard Update

The frontend retrieves fresh data through:

```text
Browser
   ↓
API Gateway
   ↓
Reader Lambda
   ↓
DynamoDB
```

and updates the dashboard in real time.

---

## ⚙️ AWS Deployment Guide

### 1. Create SQS Queue

Create either:

- Standard Queue (recommended)
- FIFO Queue (strict ordering)

Example:

```text
paper-trading-queue
```

### 2. Create DynamoDB Table

Table Name:

```text
PaperTradingPortfolio
```

Partition Key:

```text
ticker (String)
```

Sort Key:

```text
timestamp (String)
```

### 3. Create Lambda Functions

Deploy:

```text
lambda_writer
lambda_reader
```

Runtime:

```text
Python 3.12
```

### 4. Configure IAM Permissions

Attach permissions:

```text
AmazonSQSFullAccess
AmazonDynamoDBFullAccess
AmazonSESFullAccess
AWSLambdaBasicExecutionRole
```

### 5. Configure SES

Verify:

- Sender email
- Recipient email

inside Amazon SES Identity Management.

### 6. Create API Gateway

Route:

```http
GET /stocks
```

Target:

```text
Reader Lambda
```

### 7. Host Frontend

Upload frontend assets to:

```text
Amazon S3
```

Enable:

```text
Static Website Hosting
```

---

## 📈 Scalability Characteristics

| Feature | Benefit |
|----------|----------|
| SQS Buffering | Handles traffic spikes |
| Lambda Auto Scaling | Supports concurrent processing |
| DynamoDB On-Demand | Automatic capacity scaling |
| API Gateway | Managed HTTP scaling |
| S3 Hosting | Virtually unlimited frontend traffic |

---

## 🎯 Learning Outcomes

This project demonstrates:

- Event-driven architecture
- Serverless computing
- Cloud-native application design
- AWS infrastructure integration
- Cost optimization strategies
- Real-time analytics pipelines
- Scalable API development
- Production-style monitoring workflows
- Lightweight machine learning deployment
- End-to-end DevOps and cloud engineering practices

---

## 📸 Future Enhancements

- WebSocket live streaming
- Amazon EventBridge integration
- Multi-stock portfolio support
- Historical trend visualization
- AWS CloudWatch dashboards
- Terraform Infrastructure as Code
- CI/CD using GitHub Actions
- Advanced ML models for anomaly detection
- User authentication with Amazon Cognito

---
## Live Demo
Link: [Trading-Dasboard](http://alen-paper-trading-dashboard-2026.s3-website.ap-south-1.amazonaws.com/)

## 👨‍💻 Author

**Alen K Aji**
