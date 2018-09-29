#!/usr/bin/python

from   __future__ import print_function
import boto3
import subprocess
import os
from os import path
import datetime
import time
import sys

#setup boto3  client
iam      = boto3.client('iam')                #setup iam client
s3       = boto3.client('s3','us-east-1')     #setup s3 client
redshift = boto3.client('redshift')           #setup s3 client
elb      = boto3.client('elb','us-east-1')    #setup elb client
elbv2    = boto3.client('elbv2','us-east-1')  #setup elbv2 application elb  client
ec2      = boto3.resource('ec2')              #setup ec2 resource
rds      = boto3.client('rds','us-east-1')    #setup rds client


#get todays date in mmddyy format
now=datetime.datetime.now()
today=now.strftime("%m%d%y")

#variables
logdir="/home/dpladmin/scripts/tmp/"

# List account aliases through the pagination interface
paginator = iam.get_paginator('list_account_aliases')
for response in paginator.paginate():
    account= str(response['AccountAliases'])
    account = account.replace("'", "").replace("[","").replace("]","")

#setup output file location
ec2filedir=logdir+today+"/"                                        # directory where script output is saved
#if directory does not exist, then create it
if not os.path.exists(ec2filedir):
   os.mkdir(ec2filedir)

ec2file=account+"-INVENTORY.csv"                                   # filename where script output is saved
fully_qualified_ec2file=ec2filedir + ec2file                       # fully qualified location of output file
fully_qualified_location_s3 = "inventory/" + today +"/" + ec2file  # fully qualified s3 path  for upload

#set S3 bucket for upload  based on AWS  account 
if   account == "aws-dataplatform":
     s3bucket = "dpl-teambucket"
elif account == "aws-engpoc":
   s3bucket = "engpoc-teambucket"
elif account == "list-aws-preclaim":
   s3bucket = "preclaim-teambucket"
elif account == "aws-myabilityportal":
   s3bucket = "myability-teambucket"
elif account == "aws-illuminate":
   s3bucket = "illuminate-teambucket"

#setup log file
log = open(fully_qualified_ec2file, "w+") 

###############################################################################
#EC2
###############################################################################

# Get list of all instances
all_instances = ec2.instances.all()

#echo headers for csv file tp log file
print ("Name,Purpose,AWS_reserved,Product,Authorization,Backups,LaunchTime,InstanceId,InstanceType,State,PublicIP,PrivateIP" , file = log)

#main loop to iterate thru each instance 
for instance in all_instances:

    #loop to get value for custom tag value attached to each instance
    for tag in instance.tags:
       if tag['Key'] == 'Name':
            name=tag['Value']
            name += " ,"               #add , 
       elif tag['Key'] == 'Purpose':
            pup=tag['Value']
            pup += " ,"                #add , 
       elif tag['Key'] == 'AWS_Reserved':
            res=tag['Value']
            res += " ,"                #add , 
       elif tag['Key'] == 'Product':
            pro=tag['Value']
            pro += " ,"                #add , 
       elif tag['Key'] == 'Authorized':
            aut=tag['Value']
            aut += " ,"                #add , 
       elif tag['Key'] == 'Backups':
            bac=tag['Value']
            bac += " ,"


    #collect ec2 specific details for each instance and append , in the end. 
    Type=instance.instance_type
    Type += " ,"
    State=instance.state['Name']
    State += " ,"
    Id=instance.id
    Id += " ,"
    PrivateIP=str(instance.private_ip_address)
    PublicIP= str(instance.public_ip_address)
    PublicIP += " ,"
    LaunchTime= str(instance.launch_time)
    LaunchTime += " ,"
    
    #echo all required values as comma separated into a file
    print (name,pup,res,pro,aut,bac,LaunchTime,Id,Type,State,PublicIP,PrivateIP , file=log)


###############################################################################
#RDS
###############################################################################
# Get list of all instances
clusters  = rds.describe_db_instances()
cluster_details = clusters['DBInstances']


print ("**********RDS Databases******************", file=log)
for cluster in cluster_details:

    cluster_name = cluster['DBClusterIdentifier']
    print (cluster_name, file=log)


###############################################################################
#REDSHIFT
###############################################################################

# Get list of all instances
clusters  = redshift.describe_clusters()

#Get cluster
cluster_details = clusters['Clusters']

#Print header for csv file
print ("**********REDSHIFT******************", file=log)

#Main
for cluster in cluster_details:
    #Get cluster name and append comma 
    cluster_id = cluster['ClusterIdentifier'] 
    cluster_id += " ,"

    #Get the tags and their values
    for tag in cluster['Tags']:
       if tag['Key'] == 'Authorized':
            aut=tag['Value']
       elif tag['Key'] == 'Purpose':
            pup=tag['Value']
            pup += " ,"
       elif tag['Key'] == 'AWS_Reserved':
            res=tag['Value']
            res += " ,"
       elif tag['Key'] == 'Product':
            pro=tag['Value']
            pro += " ,"
    #Print output to csv file
    print (cluster_id,pup,res,pro,aut , file=log)

###############################################################################
#ELB
###############################################################################
# Get list of all instances
elblist    = elb.describe_load_balancers()
elblistv2  = elbv2.describe_load_balancers()

#print header to output file 
print( "**********ELASTIC LOAD BALANCER *****************" , file=log)

for elbs in elblist['LoadBalancerDescriptions']:
    elbname = elbs['LoadBalancerName']
    print (elbname , file=log)

for elbsv2 in elblistv2['LoadBalancers']:
    elbnamev2 = elbsv2['LoadBalancerName']
    print (elbnamev2 , file=log)


###############################################################################
#S3
###############################################################################

#print headers for csv file
print ("**********S3 BUCKETS******************" , file=log)
print ("BucketName,Purpose,PHI_DATA,Product,Authorized,Creation_Date" 	, file=log)

# Get list of all Buckets
buckets  = s3.list_buckets()

#Loop thru each bucket 
for b in  buckets['Buckets']:
    bucketname = str(b['Name'])                            #get bucket name
    ctime     =  b['CreationDate']                         #get bucket creation time
    bucketags = s3.get_bucket_tagging(Bucket = bucketname) #get all the custome tags for the bucket

    #get values for tags we need for csv file
    for tag in bucketags['TagSet']:
       if tag['Key'] == 'Purpose':
            pup=tag['Value']
            pup+= " ,"
       elif tag['Key'] == 'PHI_Data':
            phi=tag['Value']
            phi += " ,"
       elif tag['Key'] == 'Product':
            pro=tag['Value']
            pro += " ,"
       elif tag['Key'] == 'Authorized':
            aut=tag['Value']
            aut += " ,"
    #print output to csv file 
    bucketname += " ,"
    print (bucketname,pup,phi,pro,aut,ctime , file=log)


##########################################################################################
########### END OF DATA COLLECTION #######################################################
##########################################################################################

#close the log file
log.close()

#S3 UPLOAD PHASE
#upload file to s3 bucket
data = open(fully_qualified_ec2file, 'rb')   #open output for reading
s3.put_object(Bucket=s3bucket, Key=fully_qualified_location_s3, Body=data) # upload file to s3

#test 
#os.system("/home/kmokha/PY/a")
