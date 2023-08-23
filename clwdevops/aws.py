import logging

import boto3
import botocore

s3c = boto3.client("s3")
s3r = boto3.resource("s3")
log = logging.getLogger(__name__)


def get_s3_object(bucket: str, key: str) -> bytes:
    """Retrieve s3 object as bytes"""
    bkt = s3r.Bucket(bucket)
    obj = bkt.Object(key).get()
    return obj["Body"].read()


def download_s3_object(bucket: str, key: str, dst: str):
    """Download s3 file to destination"""
    try:
        s3c.download_file(bucket, key, dst)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            log.info(f"{bucket}/{key} does not exist")
        else:
            raise
    return


def put_s3_object(bucket: str, key: str, data: bytes):
    """Upload data to s3 bucket/key"""
    try:
        s3c.put_object(Bucket=bucket, Key=key, Body=data)
        log.info(f"Uploaded to {bucket}/{key}")
    except Exception as e:
        log.info("Failed to upload to s3")
        raise (e)


def list_s3_files(bucket: str, prefix: str, suffix: str) -> list:
    """List all files in s3 bucket/prefix with suffix"""
    bkt = s3r.Bucket(bucket)
    files = [
        f"s3://{bkt}/{x.key}" for x in bkt.objects.filter(Prefix=prefix) if x.key.endswith(suffix)
    ]
    return files


def is_s3_object(bucket, key):
    """Check if s3 object exists"""
    try:
        s3c.head_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError:
        return False
    else:
        return True
