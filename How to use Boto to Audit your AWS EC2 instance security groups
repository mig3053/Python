#!/usr/bin/env python
__author__ = 'Jason Riedel'
__description__ = 'Find EC2 instances provisioned in a public subnet that have security groups allowing ingress traffic from any source.'
__date__ = 'June 5th 2016'
__version__ = '1.0'
 
import boto3
 
def find_public_addresses(ec2):
    public_instances = {}
    instance_public_ips = {}
    instance_private_ips = {}
    instance_ident = {}
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running'] }])
 
    # Ranges that you define as public subnets in AWS go here.
    public_subnet_ranges = ['10.128.0', '192.168.0', '172.16.0']
 
    for instance in instances:
        # I only care if the private address falls into a public subnet range
        # because if it doesnt Internet ingress cant reach it directly anyway even with a public IP
        if any(cidr in instance.private_ip_address for cidr in public_subnet_ranges):
            owner_tag = "None"
            instance_name = "None"
            if instance.tags:
                for i in range(len(instance.tags)):
                    #comment OwnerEmail tag out if you do not tag your instances with it.
                    if instance.tags[i]['Key'] == "OwnerEmail":
                        owner_tag = instance.tags[i]['Value']
                    if instance.tags[i]['Key'] == "Name":
                        instance_name = instance.tags[i]['Value']
            instance_ident[instance.id] = "Name: %s\n\tKeypair: %s\n\tOwner: %s" % (instance_name, instance.key_name, owner_tag)
            if instance.public_ip_address is not None:
                values=[]
                for i in range(len(instance.security_groups)):
                    values.append(instance.security_groups[i]['GroupId'])
                public_instances[instance.id] = values
                instance_public_ips[instance.id] = instance.public_ip_address
                instance_private_ips[instance.id] = instance.private_ip_address
 
    return (public_instances, instance_public_ips,instance_private_ips, instance_ident)
 
def inspect_security_group(ec2, sg_id):
    sg = ec2.SecurityGroup(sg_id)
 
    open_cidrs = []
    for i in range(len(sg.ip_permissions)):
        to_port = ''
        ip_proto = ''
        if 'ToPort' in sg.ip_permissions[i]:
            to_port = sg.ip_permissions[i]['ToPort']
        if 'IpProtocol' in sg.ip_permissions[i]:
            ip_proto = sg.ip_permissions[i]['IpProtocol']
            if '-1' in ip_proto:
                ip_proto = 'All'
        for j in range(len(sg.ip_permissions[i]['IpRanges'])):
            cidr_string = "%s %s %s" % (sg.ip_permissions[i]['IpRanges'][j]['CidrIp'], ip_proto, to_port)
 
            if sg.ip_permissions[i]['IpRanges'][j]['CidrIp'] == '0.0.0.0/0':
                #preventing an instance being flagged for only ICMP being open
                if ip_proto != 'icmp':
                    open_cidrs.append(cidr_string)
 
    return open_cidrs
 
 
if __name__ == "__main__":
    #loading profiles from ~/.aws/config & credentials
    profile_names = ['de', 'pe', 'pde', 'ppe']
    #Translates profile name to a more friendly name i.e. Account Name
    translator = {'de': 'Platform Dev', 'pe': 'Platform Prod', 'pde': 'Products Dev', 'ppe': 'Products Prod'}
    for profile_name in profile_names:
        session = boto3.Session(profile_name=profile_name)
        ec2 = session.resource('ec2')
 
        (public_instances, instance_public_ips, instance_private_ips, instance_ident) = find_public_addresses(ec2)
 
        for instance in public_instances:
            for sg_id in public_instances[instance]:
                open_cidrs = inspect_security_group(ec2, sg_id)
                if open_cidrs: #only print if there are open cidrs
                    print "=================================="
                    print " %s, %s" % (instance, translator[profile_name])
                    print "=================================="
                    print "\tprivate ip: %s\n\tpublic ip: %s\n\t%s" % (instance_private_ips[instance], instance_public_ips[instance], instance_ident[instance])
                    print "\t=========================="
                    print "\t open ingress rules"
                    print "\t=========================="
                    for cidr in open_cidrs:
                        print "\t\t" + cidr
