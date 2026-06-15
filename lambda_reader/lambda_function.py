import json
import boto3

# Using the client to avoid Pylance warnings, just like our writer!
dynamodb_client = boto3.client('dynamodb', region_name='ap-south-1')
TABLE_NAME = 'PaperTradingPortfolio'

def lambda_handler(event, context):
    try:
        # Scan pulls everything from the table. 
        # (Fine for our small project, though large enterprise tables use 'Query' instead)
        response = dynamodb_client.scan(TableName=TABLE_NAME)
        items = response.get('Items', [])
        
        # DynamoDB uses strict type formatting ('S' for string, 'N' for number)
        # We need to clean this up so our frontend gets normal, readable JSON
        # ... (previous code above remains the same)
        clean_data = []
        for item in items:
            clean_data.append({
                'ticker': item['ticker']['S'],
                'timestamp': item['timestamp']['S'],
                'price': float(item['price']['S']),
                'volume': int(item['volume']['N']),
                # Safely grab the boolean, default to False for old records
                'is_anomaly': item.get('is_anomaly', {}).get('BOOL', False) 
            })
        
        clean_data.sort(key=lambda x: x['timestamp'], reverse=True)
        # ... (return statement below remains the same)
        # Sort the data by timestamp so the newest trades appear first
        clean_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', # CRITICAL: This allows a web browser to read the data
                'Content-Type': 'application/json'
            },
            'body': json.dumps(clean_data)
        }
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to fetch data from database.'})
        }
