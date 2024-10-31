''' Script to generate a client for MinIO S3. '''
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from jobs.config.security_variables import MINIO_ENDPOINT, MINIO_PASSWORD, MINIO_USER

def s3_client():
    ''' Function to generate a client for MinIO S3. '''
    try:
        return boto3.client(
            's3',
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_USER,
            aws_secret_access_key=MINIO_PASSWORD
        )
    except (BotoCoreError, ClientError) as e:
        print(f"Error creating S3 client: {e}")
        raise

