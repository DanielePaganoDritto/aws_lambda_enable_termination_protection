# EAR-IT-Lambda-EnableTerminationProtection.py

Python Lambda Function than scans all the resources inside an account enabling the Termination Protection option on the one for which it is disabled.

The purpose is to periodically check all this instances and autoimatically set the same attribute to True in order to avoid accidental instances deletion.

&nbsp;

## SNS Notifications
After every function run the template send an email to an SNS Topic containing a confirmation message for the execution.

For this to work is necessary to pass the Topic Arn and the AWS Account description  to which send the notification by creating a test event before running the Lambda function. The test event should have the following structure:

&nbsp;

{
"TopicArn": "arn:aws:sns:::",
"AccountDescription": ""
}

&nbsp;

## IAM Role and Policy
To run the Lambda function you need ti create/use an IAM Role with the following policies to interact with all the resources needed:

- Role Name: AWSLambdaCheckTerminationProtection
- Role Policy: 
    - Policy 1 Name: Ec2-AWSLambdaCheckTerminationProtection
        - EC2 ReadOnly
        - EC2 ModifyInstanceAttribute

    - Policy 2 Name: SNS-AWSLambdaCheckTerminationProtection
        - SNS Publish

    - Policy 3 Name: ELB-AWSLambdaCheckTerminationProtection
        - DescribeLoadBalancers
        - DescribeLoadBalancerAttributes
        - ModifyLoadBalancerAttributes

    - Policy 4 Name: RDS-AWSLambdaCheckTerminationProtection
        - DescribeDBInstances
        - ModifyDBInstance

&nbsp;

** N.B The example ARN above refers to the Topic ARN for Cloud Team Notifications configured in the Core Services account. Change it accordingly when creating the Lambda function on any different account. **