import boto3

# Initialize the S3 client using the IAM role credentials
s3 = boto3.client('s3')

# S3 bucket and object key where the .env file is located
s3_bucket = 'majestic-env'
s3_object_key = '.env'

# Download the .env file from S3
s3.download_file(s3_bucket, s3_object_key, '.env')