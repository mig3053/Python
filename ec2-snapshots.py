#!/usr/bin/env python

from   __future__ import print_function
import boto3
import time
import datetime
import argparse

#set command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--role')
parser.add_argument('--days', type=int, default=7)
args = parser.parse_args()

#get todays date in mmddyy format
now=datetime.datetime.now()
today=now.strftime("%m%d%y")

#setup client
ec2 = boto3.client('ec2')

# get list of all volumes which are tagged with --role
result = ec2.describe_volumes( Filters=[{'Name': 'tag:Role', 'Values': [args.role]}])

#setup log file for snapshots 
fully_qualified_snapshot_log="/home/dplbackups/scripts/log/snapshot_log"
log = open(fully_qualified_snapshot_log, "a")

# Now iterate for each volume
print ("++Starting Snapshots for volume tag : " +args.role +" on "  +today ,file=log)

for volume in result['Volumes']:

# Create snapshot and store in result 
 result = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description='Created  by ebs-snapshots python script')

# Now get the snapshot id from the results
 ec2resource = boto3.resource('ec2')
 snapshot = ec2resource.Snapshot(result['SnapshotId'])
 
# Find name tag for volume if it exists
 if 'Tags' in volume:
  for tags in volume['Tags']:
   if tags["Key"] == 'Name':
    volumename = tags["Value"]
    print ("+Creating snapshot of volume :" +volumename ,file=log)
    volumename = (str(volumename) + "-snapshot")

# Add snapshot tags  for easier identification
 snapshot.create_tags(Tags=[{'Key': 'Name','Value': volumename}])
 snapshot.create_tags(Tags=[{'Key': 'Role','Value': args.role}])
 snapshot.create_tags(Tags=[{'Key': 'Product','Value': "DPL"}])
 snapshot.create_tags(Tags=[{'Key': 'PurgeAllow','Value': "True"}])

print (" ", file=log)
log.close()
#end snapshot script


#Snapshot Delete 

#setup client 
client = boto3.client('ec2')

#get AWS account
account_id=boto3.client('sts').get_caller_identity()['Account']

#setup log file 
fully_qualified_snapshot_delete_log="/home/dplbackups/scripts/log/snapshot_delete_log"
log = open(fully_qualified_snapshot_delete_log, "a")

#get list of snapshots
snapshots = client.describe_snapshots()
snapshots = client.describe_snapshots(OwnerIds=[account_id])
print ("++Deleted Snapshot(s) for volume tag : " +args.role +" on: " +today  ,file=log)

#loop thru snapshots for deletion based on --days and --role tag
for snapshot in snapshots['Snapshots']:
       a= snapshot['StartTime']
       b=a.date()
       c=datetime.datetime.now().date()
       d=c-b
       try:
        if d.days>args.days:
           id = snapshot['SnapshotId']
           for tags in snapshot['Tags']:
             if tags["Key"] == 'Role':
               roletag = tags["Value"]
               if roletag == args.role:
                 client.delete_snapshot(SnapshotId=id)
                 print ("+snapshot_id: "+id, file=log)

       except Exception,e:
        if 'InvalidSnapshot.InUse' in e.message:
           print ("skipping snapshot_id:"+id, file=log)
           continue



print (" ", file=log)
log.close()
#end of Delete 

#end of script
