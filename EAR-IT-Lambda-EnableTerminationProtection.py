import json 
import boto3 
import datetime 
 
from collections import defaultdict 
 
#Create an EC2 resource 
ec2 = boto3.resource('ec2') 
 
#Create an EC2 client 
client = boto3.client('ec2') 
 
#Create an ELB client 
elb = boto3.client('elbv2') 
 
#Create RDS Client 
rds_db = boto3.client('rds') 
 
# Create an SNS client 
sns = boto3.client('sns') 
 
def lambda_handler(event, context): 
 
    # Get information for all running instances 
    running_instances = ec2.instances.filter() 
 
    ec2info = defaultdict() 
    for instance in running_instances: 
         
        name="" 
        description="" 
         
        #restrieve tag Name and Description values 
        for tag in instance.tags: 
            if 'Name'in tag['Key']: 
                name = tag['Value'] 
            if 'Description' in tag['Key']: 
                description = tag['Value'] 
        terminate_protection = instance.describe_attribute(Attribute = 'disableApiTermination') 
        protection_value=(terminate_protection['DisableApiTermination']['Value']) 
         
        #Check Only Instances with Termination Protection Disabled  
        if protection_value == False: 
 
            # List instances with termination protection disabled 
            ec2info[instance.id] = { 
                'Name': name, 
                'Description': description, 
                'Type': instance.instance_type, 
                'State': instance.state['Name'], 
                'Private IP': instance.private_ip_address, 
                'Termination Protaction' : protection_value 
            } 
 
            instance.modify_attribute(DisableApiTermination={'Value': True}) 
 
    attributes = ['Name', 'Description','Type', 'State', 'Private IP', 'Termination Protaction'] 
 
    
    #Print Results 
    for instance_id, instance in ec2info.items(): 
        print("------") 
        print("EC2 Instances:") 
        for key in attributes: 
            print("{0}: {1}".format(key, instance[key])) 
        print("------") 
 
    #Scan existng Load Balancers 
    existing_loadbalancers = elb.describe_load_balancers() 
     
    #Get the ARN of each existing load balancer     
    print("------") 
    print ("Load Balancers ARN:") 
    for loadbalancers in existing_loadbalancers["LoadBalancers"]: 
        loadbalancerArn = loadbalancers["LoadBalancerArn"] 
        print (loadbalancerArn) 
         
        #Scan the attributes of each LoadBalancer 
        loadBalancer_attributes=elb.describe_load_balancer_attributes(LoadBalancerArn=loadbalancerArn) 
     
        elb_termination_protection='' 
        for attribute_key in loadBalancer_attributes["Attributes"]: 
            if 'deletion_protection.enabled'in attribute_key['Key']: 
                elb_termination_protection = attribute_key['Value'] 

            if elb_termination_protection == "false": 
                print("Termination Protection: ",elb_termination_protection)
                elb.modify_load_balancer_attributes(LoadBalancerArn=loadbalancerArn, Attributes=[{'Key': 'deletion_protection.enabled', 'Value': "true"}]) 
                 
    #Scan existng RDS DB Instances 
    existing_rds_db = rds_db.describe_db_instances() 
    
    print("------") 
    print ("RDS:") 
    for rds_db_instances in existing_rds_db['DBInstances']: 
        rds_name = rds_db_instances["DBInstanceIdentifier"] 
        rds_termination_protection = rds_db_instances["DeletionProtection"] 
        if rds_termination_protection == False:
            print("DB Name: ",rds_name) 
            print("Deletion Protection:", rds_termination_protection)  
            rds_db.modify_db_instance(DBInstanceIdentifier=rds_name,DeletionProtection=True) 
            print ("Instance modified") 
            print("------") 
     
    #Prepare SNS message 
    SFCAccount=event['AccountDescription'] 
    message = ("Termination protection enabled for account: %s" % SFCAccount) 
    subject = ("Lambda Function - Termination protection enabled for account %s" % SFCAccount) 
     
    #Send notification     
    sns.publish(TopicArn=event['TopicArn'], Message=(message), Subject=(subject)) 