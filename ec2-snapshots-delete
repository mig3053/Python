#!/usr/bin/python

from   __future__ import print_function
import boto3
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--days', type=int, default=7)
parser.add_argument('--role')
args = parser.parse_args()
print (args.days)
print (args.role)

account_id=boto3.client('sts').get_caller_identity()['Account']

#get todays date in mmddyy format
now=datetime.datetime.now()
today=now.strftime("%m%d%y")


fully_qualified_snapshot_delete_log="/home/dpladmin/scripts/tmp/snapshot_delete_log"
log = open(fully_qualified_snapshot_delete_log, "a")
print ("++  Deleted Snapshot(s) on:" +today  ,file=log)

client = boto3.client('ec2')
snapshots = client.describe_snapshots()
snapshots = client.describe_snapshots(OwnerIds=[account_id])
for snapshot in snapshots['Snapshots']:
       a= snapshot['StartTime']
       b=a.date()
       c=datetime.datetime.now().date()
       d=c-b
       try:
        if d.days>args.days:
           id = snapshot['SnapshotId']
          # client.delete_snapshot(SnapshotId=id)
           print ("snapshot_id:"+id, file=log)
       except Exception,e:
        if 'InvalidSnapshot.InUse' in e.message:
           print ("skipping snapshot_id:"+id, file=log)
           continue
print (" ", file=log)
log.close()
