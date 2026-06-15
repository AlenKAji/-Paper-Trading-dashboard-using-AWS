import json
import boto3

dynamodb_client = boto3.client('dynamodb', region_name='ap-south-1')
# Initialize the Amazon SES Client
ses_client = boto3.client('ses', region_name='ap-south-1')

TABLE_NAME = 'PaperTradingPortfolio'

# === CONFIGURATION (Change this to your verified email!) ===
SENDER_EMAIL = "allenkaji123@gmail.com"
RECEIVER_EMAIL = "allenkaji123@gmail.com"

class VolumeAnomalyDetector:
    def __init__(self):
        self.baseline_avg = 500
        self.std_dev = 200
        self.threshold_z = 2.0 
        
    def predict(self, volume):
        z_score = abs(volume - self.baseline_avg) / self.std_dev
        return bool(z_score > self.threshold_z)

ml_model = VolumeAnomalyDetector()

def send_alert_email(ticker, volume, price):
    """Helper function to compile and transmit the SES email alert"""
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECEIVER_EMAIL]},
            Message={
                'Subject': {
                    'Data': f'⚠️ MARKET ALERT: Unusual Volume Spike in {ticker}!'
                },
                'Body': {
                    'Text': {
                        'Data': (
                            f"Our AI pipeline has flagged an anomaly:\n\n"
                            f"Ticker: {ticker}\n"
                            f"Trade Volume: {volume} shares\n"
                            f"Current Price: ${price}\n\n"
                            f"This exceeds 2.0 standard deviations from normal baseline market activity."
                        )
                    }
                }
            }
        )
        print(f"Alert email dispatched successfully. MessageID: {response['MessageId']}")
    except Exception as e:
        print(f"Failed to dispatch SES email: {str(e)}")

def lambda_handler(event, context):
    success_count = 0
    
    for record in event['Records']:
        try:
            data = json.loads(record['body'])
            volume = int(data['volume'])
            ticker = str(data['ticker'])
            price = str(data['price'])
            
            is_anomaly = ml_model.predict(volume)
            
            # If the AI flags an anomaly, fire off the SES email alert instantly!
            if is_anomaly:
                print(f"🔥 Anomaly Detected for {ticker}! Invoking Amazon SES...")
                send_alert_email(ticker, volume, price)
            
            # Save data to database as usual
            dynamodb_client.put_item(
                TableName=TABLE_NAME,
                Item={
                    'ticker': {'S': ticker},
                    'timestamp': {'S': str(data['timestamp'])},
                    'price': {'S': price},
                    'volume': {'N': str(volume)},
                    'is_anomaly': {'BOOL': is_anomaly}
                }
            )
            success_count += 1
            
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            continue 
            
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {success_count} entries.')
    }
