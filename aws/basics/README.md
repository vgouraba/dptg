# dptg/aws
This is a folder to contail all sample code for AWS-Basics, such as using boto3 SDK for EC2, VPC etc.

Pre-requisites:
- Python 3.7
- Pip


Brief How-To:
1. Get the source code:
    1. git clone https://github.com/vgouraba/dptg.git
2. Setup the Python3.7 virtual env
    1. python3.7 -m venv venv
    2. source venv/bin/activate
    3. pip install boto3
3. Setup to do in EC2 before you run the program:
    1. Create a EC2 KeyPair
    2. Create a VPC with public/private subnets
4. Edit file driver.py and update the following params:
    1. "region": "us-west-2"
    2. "vpcId": ""
    3. "pubSubnetId": ""  # (public subnet ID)
    4. "pkeyName": ""  # (ec2 key pair name)
5. Once these values are set, you can run the program:
   python3.7 driver.py
