#!/usr/bin/env python

import boto3
import time
import argparse
import sys

parser = argparse.ArgumentParser()

# if no argument error out
parser.add_argument('-t','--tag',nargs='+')
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args = parser.parse_args()
newtag = str(args.tag)

ec2 = boto3.client('ec2')

# get list of all volumes which are tagged "CDHU" for cdh upgrade
result = ec2.describe_volumes( Filters=[{'Name': 'tag:Upgrade', 'Values': ['CDHUUU']}])



# Now iterate for each volume
for volume in result['Volumes']:

# Create snapshot and store in result 
 result = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description='Final snapshot before cdh upgrade')
# Add delay of 30 secs 
 time.sleep(30)


# Now get the snapshot id from the results
 ec2resource = boto3.resource('ec2')
 snapshot = ec2resource.Snapshot(result['SnapshotId'])

 
# Find name tag for volume if it exists
 if 'Tags' in volume:
  for tags in volume['Tags']:
   if tags["Key"] == 'Name':
    volumename = tags["Value"]
    volumename = (str(volumename) + "-cdh-upgrade-snapshot-" +  newtag)

# Add volume name to snapshot for easier identification
 snapshot.create_tags(Tags=[{'Key': 'Name','Value': volumename}])

