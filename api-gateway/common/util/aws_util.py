from django.conf import settings

import logging
import boto3
from botocore.exceptions import ClientError
import os
from common.util.romsg import rp

# import common.util.aws_util as aws_util
# aws_util.stop_instance('i-0539bd65024247136')
# ec2 = boto3.resource('ec2',region_name='ap-northeast-2')
#

client = boto3.client(
    'ec2',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name='ap-northeast-2'
)

def stop_instancess(instance_ids):
    response = client.stop_instances(InstanceIds=instance_ids)
    return response

def start_instances(instance_ids):
    response = client.start_instances(InstanceIds=instance_ids)
    return response

def describe_instances(instance_ids):
    return client.describe_instances(instance_ids)

def put_to_s3(bucket_name, s3_path, string):
    encoded_string = string.encode("utf-8")
    s3 = boto3.resource("s3")
    rp('S3 put: ' + bucket_name + ' ' + s3_path)
    result = s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string)
    rp('S3 put result: ' + str(result))

def upload_file(local_folder, file_name, s3_folder):
    final_file_name = local_folder + '/' + file_name
    s3_splitted = s3_folder.split('/')
    bucket = s3_splitted[0]
    object_name = '/'.join(s3_splitted[1:])
    result = _upload_file(final_file_name, bucket, object_name)
    print(result)

def _upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    print('S3 upload: ' + bucket + ' ' + object_name + ' ' + file_name)
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True