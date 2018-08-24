#!/usr/bin/python

import boto3
import subprocess
import os
import datetime


#setup boto3  client 
iam = boto3.client('iam')   #setup iam client 
s3 = boto3.client('s3')     #setup s3 client

#get todays date in mmddyy format
now=datetime.datetime.now()
today=now.strftime("%m%d%y")

#variables
inputfile="/tmp/100"
logdir="/home/dpladmin/scripts/tmp/"

# List account aliases through the pagination interface
paginator = iam.get_paginator('list_account_aliases')
for response in paginator.paginate():
    account= str(response['AccountAliases'])
    account = account.replace("'", "").replace("[","").replace("]","")

#set S3 bucket based on account 
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


###############################################################################
#MAIN
###############################################################################

# make call to generate credential report
iam.generate_credential_report()

#read  credential report and it comes as dict
report = iam.get_credential_report()

# get data from dict for  Content as string
report = report["Content"]

#read data into input temp file and close file
with open(inputfile, "w") as text_file:        # inputfile is /tmp/100
    text_file.write("%s" % report)

#setup OS command to format the generated report  and re-route output to file and run command
command = (" cat /tmp/100 | awk -F, '{print $1,$5,$6,$11,$16}' | sed 's/ / , /g' > /tmp/101.csv ") 
subprocess.call(command,  shell=True)

#setup output file location
iamfiledir=logdir+today+"/" # directory where script output is saved
iamfile=account+"-IAM.csv"  # filename where script output is saved

fully_qualified_iamfile=iamfiledir + iamfile  # fully qualified location of output file 
fully_qualified_location_s3 = "inventory/" + today +"/" + iamfile # fully qualified s3 path  for upload

#rename /tmp/101 into final output file to be pushed to s3 bucket 
os.rename("/tmp/101.csv", fully_qualified_iamfile)

#upload file to s3 bucket 
data = open(fully_qualified_iamfile, 'rb')   #open output for reading 
s3.put_object(Bucket=s3bucket, Key=fully_qualified_location_s3, Body=data) # upload file to s3

#remove temporary file
os.remove("/tmp/100")            #remove inputfile /tmp/100
