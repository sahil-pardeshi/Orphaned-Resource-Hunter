import os
import boto3
import json

def lambda_handler(event, context):
    """
    Deletes a specified orphaned resource from AWS and DynamoDB.
    
    This function expects a POST request with a JSON body containing
    'resource_id' and 'resource_type'. It handles different resource
    types (EBS, S3, etc.) and gracefully handles missing data.
    """
    try:
        # Check if a body exists and try to parse it.
        # .get() is safer than direct access like event['body']
        body_raw = event.get('body')
        
        # If the body is None or empty, return an error.
        if not body_raw:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Missing or empty request body'})
            }

        # Attempt to parse the JSON body. Catch a potential error if the JSON is malformed.
        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Invalid JSON format in request body'})
            }
        
        resource_id = body.get('resource_id')
        resource_type = body.get('resource_type')

        # Check for required fields
        if not resource_id or not resource_type:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Missing required fields: resource_id or resource_type'})
            }

        # Initialize AWS clients
        region_name = os.environ['AWS_REGION']
        table_name = os.environ['TABLE_NAME']
        sns_topic_arn = os.environ['SNS_TOPIC_ARN']
        
        ec2_client = boto3.client('ec2', region_name=region_name)
        s3_client = boto3.client('s3', region_name=region_name)
        dynamodb_client = boto3.client('dynamodb')
        sns_client = boto3.client('sns')

        # Delete the resource based on its type
        if resource_type == 'EBS Volume':
            ec2_client.delete_volume(VolumeId=resource_id)
            message = f"EBS Volume {resource_id} deleted successfully."
        elif resource_type == 'EBS Snapshot':
            ec2_client.delete_snapshot(SnapshotId=resource_id)
            message = f"EBS Snapshot {resource_id} deleted successfully."
        elif resource_type == 'S3 Bucket':
            try:
                # Check for bucket contents before attempting deletion
                response = s3_client.list_objects_v2(Bucket=resource_id)
                if 'Contents' in response:
                    message = f"S3 Bucket {resource_id} is not empty. Cannot delete."
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Access-Control-Allow-Origin': '*',
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps({'error': message})
                    }
                else:
                    s3_client.delete_bucket(Bucket=resource_id)
                    message = f"S3 Bucket {resource_id} deleted successfully."
            except Exception as e:
                s3_client.delete_bucket(Bucket=resource_id)
                message = f"S3 Bucket {resource_id} deleted successfully."
        elif resource_type == 'Elastic IP':
            ec2_client.release_address(AllocationId=resource_id)
            message = f"Elastic IP {resource_id} released successfully."
        else:
            message = f"Unsupported resource type: {resource_type}"
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': message})
            }

        # Remove the resource from DynamoDB
        dynamodb_client.delete_item(
            TableName=table_name,
            Key={'ResourceId': {'S': resource_id}}
        )

        # Publish a notification to SNS
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject=f"Orphaned Resource Deleted: {resource_id}"
        )

        # Return a success message with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': message})
        }
    except Exception as e:
        # This will catch any unexpected errors from Boto3 or other parts of the code
        print(f"Error deleting resource: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
