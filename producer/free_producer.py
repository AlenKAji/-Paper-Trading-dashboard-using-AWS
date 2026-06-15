import boto3
import json
import time
import random
from datetime import datetime

# Initialize the SQS client with your specific region
sqs_client = boto3.client('sqs', region_name='ap-south-1')

# Paste your actual SQS Queue URL here
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/456128020891/StockDataQueue' 

tickers = ['AAPL', 'MSFT', 'AMZN', 'TSLA']

def get_mock_market_data():
    """Generates simulated live stock ticks."""
    return {
        'ticker': random.choice(tickers),
        'price': round(random.uniform(100, 500), 2),
        'volume': random.randint(10, 1000),
        'timestamp': datetime.utcnow().isoformat()
    }

print("Starting free data producer. Press Ctrl+C to stop.")

try:
    while True:
        data = get_mock_market_data()
        print(f"Sending message to SQS: {data}")
        
        # Send the payload to SQS
        response = sqs_client.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(data)
        )
        
        # SQS gives back a unique MessageId for every successful send
        print(f"Successfully sent! MessageID: {response.get('MessageId')}\n")
        
        time.sleep(2) # Send a new price update every 2 seconds
        
except KeyboardInterrupt:
    print("\nProducer stopped.")
