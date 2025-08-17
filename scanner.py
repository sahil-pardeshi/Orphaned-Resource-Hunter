import os
import boto3
from datetime import datetime
import json

# Initialize the DynamoDB resource
dynamodb_resource = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Scans for orphaned resources, saves them to a DynamoDB table,
    and returns a list of all resources with CORS headers.
    """
    # Environment variables
    region_name = os.environ['AWS_REGION']
    table_name = os.environ['TABLE_NAME']

    # Initialize AWS clients
    ec2_client = boto3.client('ec2', region_name=region_name)
    s3_client = boto3.client('s3', region_name=region_name)
    efs_client = boto3.client('efs', region_name=region_name)
    
    # DynamoDB table object
    dynamodb_table = dynamodb_resource.Table(table_name)

    # List to store all orphaned resources found during the scan
    orphaned_resources = []

    # 1. Scan for Orphaned EBS Volumes
    try:
        volumes = ec2_client.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        for volume in volumes['Volumes']:
            orphaned_resources.append({
                'ResourceId': volume['VolumeId'],
                'ResourceType': 'EBS Volume',
                'Region': region_name,
                'FoundAt': datetime.now().isoformat()
            })
    except Exception as e:
        print(f"Error scanning EBS volumes: {e}")

    # 2. Scan for Orphaned EBS Snapshots
    try:
        snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])
        volume_ids = {volume['VolumeId'] for volume in ec2_client.describe_volumes()['Volumes']}
        for snapshot in snapshots['Snapshots']:
            # Check if the snapshot is not attached to an AMI
            if 'ami-' not in snapshot.get('Description', ''):
                if snapshot.get('VolumeId') not in volume_ids:
                    orphaned_resources.append({
                        'ResourceId': snapshot['SnapshotId'],
                        'ResourceType': 'EBS Snapshot',
                        'Region': region_name,
                        'FoundAt': datetime.now().isoformat()
                    })
    except Exception as e:
        print(f"Error scanning EBS snapshots: {e}")
        
    # 3. Scan for Orphaned EFS Filesystems
    try:
        filesystems = efs_client.describe_file_systems()
        for fs in filesystems['FileSystems']:
            mount_targets = efs_client.describe_mount_targets(FileSystemId=fs['FileSystemId'])
            if not mount_targets['MountTargets']:
                orphaned_resources.append({
                    'ResourceId': fs['FileSystemId'],
                    'ResourceType': 'EFS Filesystem',
                    'Region': region_name,
                    'FoundAt': datetime.now().isoformat()
                })
    except Exception as e:
        print(f"Error scanning EFS filesystems: {e}")
    
    # 4. Scan for Orphaned S3 Buckets
    try:
        buckets = s3_client.list_buckets()
        for bucket in buckets['Buckets']:
            try:
                response = s3_client.list_objects_v2(Bucket=bucket['Name'], MaxKeys=1)
                if 'Contents' not in response:
                    orphaned_resources.append({
                        'ResourceId': bucket['Name'],
                        'ResourceType': 'S3 Bucket',
                        'Region': region_name,
                        'FoundAt': datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error checking bucket {bucket['Name']}: {e}")
                continue
    except Exception as e:
        print(f"Error scanning S3 buckets: {e}")

    # 5. Scan for Orphaned Elastic IPs
    try:
        addresses = ec2_client.describe_addresses()
        for address in addresses['Addresses']:
            if 'InstanceId' not in address and 'NetworkInterfaceId' not in address:
                orphaned_resources.append({
                    'ResourceId': address['AllocationId'],
                    'ResourceType': 'Elastic IP',
                    'Region': region_name,
                    'FoundAt': datetime.now().isoformat()
                })
    except Exception as e:
        print(f"Error scanning Elastic IPs: {e}")

    # Save to DynamoDB
    if orphaned_resources:
        try:
            for resource in orphaned_resources:
                dynamodb_table.put_item(
                    Item=resource
                )
            print(f"Successfully saved {len(orphaned_resources)} orphaned resources to DynamoDB.")
        except Exception as e:
            print(f"Error writing to DynamoDB: {e}")
    
    # Get all items from DynamoDB to return to the frontend
    try:
        response = dynamodb_table.scan()
        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            response = dynamodb_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE'
            },
            'body': json.dumps({'items': items})
        }

    except Exception as e:
        print(f"Error scanning DynamoDB for response: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE'
            },
            'body': json.dumps({'error': str(e)})
        }
