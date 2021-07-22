import logging
import time

class EC2Manager:
    """
        The Class that handles the aspects of EC2
    """

    def __init__(self, logger, client, region):
        # Placeholder for the variables. Actual assignment happens in the init_vars method
        # This is to eliminate the warning: "Instance attribute <var> defined outside __init__"
        self.logger = logging.getLogger()
        self.client = client
        self.region = region

        # set AMI ID based on region
        ami_dict = {"us-east-1": 'ami-0323c3dd2da7fb37d',
                         "us-east-2": 'ami-0f7919c33c90f5b58',
                         "us-west-1": 'ami-06fcc1f0bc2c8943f',
                         "us-west-2": 'ami-0d6621c01e8c2de2c'
                         }
        self.ami_id = ami_dict.get(self.region)  # may get None if any other region is passed
        self.logger.info("AMI to use: %s", self.ami_id)

        self.sg_name = "dptg-sg"
        self.max_loop_counter = 30

    # create a new SG to be used by the new Jump Host
    def __create_security_group(self, vpc_id, sg_name):
        """  creates a SG inside VPC. Returns ID of the SG """
        self.logger.info("Method Entry. sg_name '%s' vpc_id '%s'", sg_name, vpc_id)

        sec_group = self.client.create_security_group(GroupName=sg_name,
                                                      Description='SG for Jump Temp Credential',
                                                      VpcId=vpc_id)
        self.logger.info("Sec Group created: %s", sec_group['GroupId'])
        return sec_group['GroupId']

    # add inbound ports to the sec group of jump hosts. These  are the ports needed for BT PasswordSafe
    def __add_sg_ingres_for_psafe(self, sg_id):
        """  Sets up Jump Host SG ingres ports for the BT appliance. void Return """
        self.logger.info("Method Entry. sg_id '%s'", sg_id)

        self.client.authorize_security_group_ingress(GroupId=sg_id, IpProtocol='tcp', FromPort=22,
                                                     ToPort=22, CidrIp="0.0.0.0/0")

    # creates a new EC2 instance for the Jump Host
    # Returns (PublicIP, PublicDNS, Private IP, InstanceID)
    def __start_ec2_instance(self, pkey_name, pub_subnet_id, sg_id, ami_id, name_tag, inst_type="t2.micro"):
        """
        Starts the new EC2 jump host
        @return: Returns PublicIP, PublicDNS, Private IP, InstanceID
        """
        self.logger.info("Method Entry. pkey '%s' pub_subnet_id '%s' sg_id '%s' ami_id '%s'",
                         pkey_name, pub_subnet_id, sg_id, ami_id)

        # define Network Interface attrs
        nwk_if_dict = {'AssociatePublicIpAddress': True, 'DeviceIndex': 0,
                       'SubnetId': pub_subnet_id, 'Groups': [sg_id]}

        # lets setup some Tags, so they'd be useful when decommissioning
        tags = [{'ResourceType': 'instance',
                 "Tags": [{"Key": "Name", "Value": name_tag}]
                }]

        # Handle possible exception thrown by AWS
        """
        [ERROR] ClientError: An error occurred (InsufficientInstanceCapacity) when calling the RunInstances
        operation (reached max retries: 4): We currently do not have sufficient t2.xlarge capacity in the
        Availability Zone you requested (us-east-2c). Our system will be working on provisioning additional capacity.
        """

        ec2_out = None
        # we can provide either network interface or subnet/secgroup.
        # However, needed to use NetworkInterface so we can assign a public IPv4
        try:
            ec2_out = self.client.run_instances(ImageId=ami_id, InstanceType=inst_type,
                                                KeyName=pkey_name, MaxCount=1, MinCount=1,
                                                NetworkInterfaces=[nwk_if_dict], TagSpecifications=tags
                                                )
        except:
            self.logger.info(f"Exception in creating {inst_type} type jump host.")

        # if failed to create instance, try default t2.large type as a fallback option
        if ec2_out is None:
            try:
                ec2_out = self.client.run_instances(ImageId=ami_id, InstanceType='t2.large',
                                                    KeyName=pkey_name, MaxCount=1, MinCount=1,
                                                    NetworkInterfaces=[nwk_if_dict], TagSpecifications=tags
                                                    )
            except:
                self.logger.info("Exception in creating t2.large type jump host.")

        self.logger.debug("EC2 Run output: %s", ec2_out)
        # both tries did not work, unable to create the instance...so stop the process
        if ec2_out is None:
            return None

        instance_id = ec2_out['Instances'][0]['InstanceId']
        self.logger.info("EC2 instance ID: %s", instance_id)

        # In order to get the IPs, needed to wait until the instance state becomes running.
        # Doing it in a loop. Is there a better way?
        ec2_info = self.__wait_for_ec2_state(instance_id, "running")

        # Even if the instance is not fully 'running' state, it should still have the following values
        ec2_private_ip = ec2_info['Reservations'][0]['Instances'][0]['PrivateIpAddress']
        ec2_public_ip = ec2_info['Reservations'][0]['Instances'][0]['PublicIpAddress']
        ec2_public_dns = ec2_info['Reservations'][0]['Instances'][0]['PublicDnsName']
        self.logger.info("EC2 Instance PublicIP: %s PublicDNS: %s and PrivateIP: %s",
                         ec2_public_ip, ec2_public_dns, ec2_private_ip)

        return ec2_public_ip, ec2_public_dns, ec2_private_ip, instance_id

    # Create Jump host and Asset in PSafe - Linux SSH
    def __create_jump_ec2_linux(self, vpc_id, inst_type, name_tag, pkey_name, pub_subnet_id):
        """
        Create a new Jump host for Linux SSH
        :return: ec2_info
        """
        self.logger.info("Method Entry.pkey_name: %s, pub_subnet_id: %s", pkey_name, pub_subnet_id)

        secgrp_id = self.__create_security_group(vpc_id, self.sg_name)
        self.logger.info("Sec Group ID: %s", secgrp_id)


        ec2_info = None
        # ec2_info will have [ec2_public_ip, ec2_public_dns, ec2_private_ip, instance_id]
        ec2_info = self.__start_ec2_instance(pkey_name, pub_subnet_id, secgrp_id, self.ami_id, name_tag, inst_type)
        self.logger.debug("Linux Jump EC2 Details: %s", ec2_info)

        if ec2_info is None:
            return None, None

        return ec2_info

    # check if EC2 instance desired status (running or terminated). Do this for max tries
    # we could use waiter on resource, but chose to do this in a loop, so it doesn't block for a long time
    def __wait_for_ec2_state(self, instance_id, status):
        """ wait in a loop until new EC2 state becomes input status of 'running' or 'terminated'.
            Returns ec2_info """
        self.logger.info("Method Entry. Check for instance:%s for status '%s'", instance_id, status)

        counter = 0
        ec2_info = None
        while counter < self.max_loop_counter:
            time.sleep(10)
            ec2_info = self.client.describe_instances(InstanceIds=[instance_id])
            self.logger.debug("EC2 Info: %s", ec2_info)
            ec2_state = ec2_info['Reservations'][0]['Instances'][0]['State'].get('Name')
            self.logger.info("ec2 instance %s and state = %s", instance_id, ec2_state)  # so we can see the status
            counter = counter + 1
            if ec2_state == status:
                break

        # its still possible that we may reach here running out of max loop counter.
        # Caller is responsible to handle it.
        return ec2_info

    def create_jump_ec2(self, vpc_id, inst_type, name_tag, pub_subnet_id, pkey_name):
        return  self.__create_jump_ec2_linux(vpc_id, inst_type, name_tag, pkey_name, pub_subnet_id)

