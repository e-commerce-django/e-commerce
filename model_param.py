import boto3
import botocore

s3_uri = 's3://sagemaker-studio-271537232646-3b2rsg9mnnu/models/recommendation/bert_model.pth'
bucket_name = s3_uri.split('/')[2]
object_key = '/'.join(s3_uri.split('/')[3:])

local_model_path = './bert_model.pth'

session = boto3.Session()

s3 = session.client('s3')

try:
    # Download the file
    s3.download_file(bucket_name, object_key, local_model_path)
    print(f"File downloaded successfully to: {local_model_path}")
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        print("Error occurred:", e)