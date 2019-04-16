#!/usr/bin/python

import boto3
import argparse
import sys

#set command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--profile')
args = parser.parse_args()

#check if one arguments has been passed
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()
print args

#setup session with profile provided
session = boto3.session.Session(profile_name=args.profile)

# Prompt for MFA time-based one-time password (TOTP)
mfa_TOTP = raw_input("Enter the MFA code: ")

# The calls to AWS STS GetSessionToken must be signed with the access key ID and secret
# access key of an IAM user. The credentials can be in environment variables or in
# a configuration file and will be discovered automatically
# by the STSConnection() function. For more information, see the Python SDK
# documentation: http://boto.readthedocs.org/en/latest/boto_config_tut.html

client = session.client('sts')

response = client.get_session_token( DurationSeconds=3600, SerialNumber='arn:aws:iam::1111111111111:mfa/xxxx@hotmail.com', TokenCode=mfa_TOTP )

aws_access_key_id=response['Credentials']['AccessKeyId']
aws_secret_access_key=response['Credentials']['SecretAccessKey']
aws_session_token=response['Credentials']['SessionToken']

iam=boto3.client('iam',  aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)

# List account aliases through the pagination interface
paginator = iam.get_paginator('list_account_aliases')
for response in paginator.paginate():
    account= str(response['AccountAliases'])
    account = account.replace("'", "").replace("[","").replace("]","")
    print(account)
