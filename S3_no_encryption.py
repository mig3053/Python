#!/usr/bin/env python

"""

A simple script to get encryption information about S3 buckets.


Eduardo Meza for Mckinsey.

"""

import boto3
import json
from accounts import accounts
from boto3.session import Session
import csv
from botocore.exceptions import ClientError


filename = "Buckets_Without_Encryption"
output_csv = open(filename+'.csv', 'w')
output_csv.write('ACCOUNT, BUCKET, ENCRYPTION\n')
fields = ['Account', 'Region', 'Instance_Id']
bad_counter=0

regions = {'us-east-1'} # S3 is global. No need to iterate over all regions.

for account in accounts:
    for region in regions:

### Assume role block:

        print('-------')
        print('Checking: '+str(account)+'\n')
        try:
            session = boto3.Session(profile_name=account, region_name=region)
            s3 = session.client('s3')
            response = s3.list_buckets()

### Looking for bad buckets block:

            for bucket in response['Buckets']:
                try:
                    enc = s3.get_bucket_encryption(Bucket=bucket['Name'])
                    rules = enc['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']
                    if rules == "AES256":
                        rules = "Default AWS encryption"
                    elif rules == "aws:kms":
                        rules = "Custom key"
                    print('Bucket: %s, Encryption: %s' % (bucket['Name'], rules))
                    data = (str(account) + ',' +str(bucket['Name']) + ',' + str(rules)) # => I dont want to write good buckets to the CSV file
                    output_csv.write(data + '\n')
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                        rules = "No encryption"
                        data = (str(account) + ',' +
                            str(bucket['Name']) + ',' + 
                            str(rules))
                        output_csv.write(data + '\n')
                        print('Bucket: %s, no server-side encryption' % (bucket['Name']))
                        bad_counter += 1

### Remediation block:  

                        # s3.put_bucket_encryption(
                        #     Bucket=(bucket['Name']),
                        #     #ContentMD5=hash,
                        #     ServerSideEncryptionConfiguration={
                        #         'Rules': [
                        #             {
                        #                 'ApplyServerSideEncryptionByDefault': {
                        #                     'SSEAlgorithm': 'aws:kms',  # => ARGS: 'AES256' |'aws:kms',
                        #                     'KMSMasterKeyID': '5337cbfd-0449-42fb-ab22-38e85c845984'  # => Enable it in case of custom KMS
                        #                 }
                        #             },
                        #         ]
                        #     }
                        # )
                        # print('Bucket has been remediated with KMS default encryption.')
                    else:
                        print("Bucket: %s, unexpected error: %s" % (bucket['Name'], e))               
        except Exception as e:
            print(e)
            pass
if bad_counter == 0:
    print('No offender buckets found!!!')


