
import configparser
import os
import sys

from google.cloud import storage
from configparser import ConfigParser

from google.cloud.storage import blob


class GStorage():

    def __init__(self, config):
        configs = ConfigParser()
        configs.read(config)
        gauth_json = configs.get('gstorage', 'auth_json')
        self.gclient = storage.Client.from_service_account_json(gauth_json)
        gbuckets = list(self.gclient.list_buckets())
        self.bilge_buckets = []
        for bucket in gbuckets:
            bstr = str(bucket).split(':')
            bucket_name = bstr[1].replace('<', '').replace('>', '').strip()
            self.bilge_buckets.append(bucket_name)

    def gs_checkbucket(self, bucket):
        if bucket in self.bilge_buckets:
            return True
        else:
            return False

    # Create a bucket
    def gs_createbucket(self, bucket_name):
        bucket = self.gclient.bucket(bucket_name)
        bucket.storage_class = "COLDLINE"
        new_bucket = self.gclient.create_bucket(bucket, location="US-CENTRAL1")

    def gs_upload(self, bucket, file_path):  # Client ID is the same as the folder name
        pathname = file_path.split('/')
        filename = pathname[-1]
        bucket_obj = self.gclient.bucket(bucket)
        upload_filename = bucket_obj.blob(filename)
        upload_filename.upload_from_filename(file_path)
        #print(f'File {file_path} copied to {bucket}')

    def gs_delete(self, bucket, file_obj):
        bucket_obj = self.gclient.bucket(bucket)
        blob = bucket_obj.blob(file_obj)
        blob.delete()
        #print(f'File {file_obj} deleted from {bucket}')
