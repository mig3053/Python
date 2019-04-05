#!/usr/local/bin/python3
######################################################################################################################
# Purpose:      Search security groups with specific rules and network interfaces using these security groups        #
# Input Params: None                                                                                                 #
# Usage:        ./nic_sg_open.py   [python ./nic_sg_open.py]                                                                 #
# Author:       Abdul M. Gill                                                                                        #
# Doc. Ref:     http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_security_groups#
######################################################################################################################
from __future__ import print_function

import json
import boto3

#Explicitly declaring variables here grants them global scope
cidr_block = ""
ip_protpcol = ""
from_port = ""
to_port = ""
from_source = ""
open_sg = []
nic_sg = []
culprit_sg = False

for region in ["us-east-1","us-west-1", "us-west-2"]:
	ec2=boto3.client('ec2', region )
	network_inerfaces = ec2.describe_network_interfaces()
	#Filter by inbound protocol=all, inbound source ip=any
	sgs = ec2.describe_security_groups(
		Filters=[
        	{
            	'Name': 'ip-permission.cidr',
            	'Values': [
                	'0.0.0.0/0',
					'::/0'
            	]
        	},
			{
            	'Name': 'ip-permission.protocol',
            	'Values': [
                	'-1',
            	]
        	}
    	]
	)["SecurityGroups"]

	# Filter by inbound protocol=all, inbound source ip=any
	# sgs = ec2.describe_security_groups(
	# 	Filters=[
    #     	{
    #         	'Name': 'ip-permission.cidr',
    #         	'Values': [
    #             	'0.0.0.0/0',
	# 				'::/0'
    #         	]
    #     	},
	# 		{
    #         	'Name': 'ip-permission.port',
    #         	'Values': [
    #             	'22',
    #         	]
    #     	}
    # 	]
	# )["SecurityGroups"]

	for sg in sgs:
		group_name = sg['GroupName']
		group_id = sg['GroupId']
		# InBound permissions ##########################################
		inbound = sg['IpPermissions']
		for rule in inbound:
			if rule['IpProtocol'] == "-1":
				if len(rule['IpRanges']) > 0:
					for ip_range in rule['IpRanges']:
						if ip_range['CidrIp'] == "0.0.0.0/0":
							culprit_sg = True
							continue
				if len(rule['Ipv6Ranges']) > 0:
					for ip_range in rule['Ipv6Ranges']:
						if ip_range['CidrIpv6'] == "::/0":
							culprit_sg = True
							continue
			if culprit_sg:
				continue
		if culprit_sg:
			open_sg.append(group_id)

	for nic in network_inerfaces['NetworkInterfaces']:
		for group in nic['Groups']:
			if group['GroupId'] in open_sg:
				nic_sg.append(nic['NetworkInterfaceId'])
				continue

print (open_sg)
print (nic_sg)
