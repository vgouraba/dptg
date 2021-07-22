import logging
import boto3

from ec2mgr import EC2Manager
from ssmmgr import SSMManager


class AWSDriver:
    """
        The main program that handles the AWS related activities
    """

    def __init__(self):
        # Placeholder for the variables. Actual assignment happens in the init_vars method
        # This is to eliminate the warning: "Instance attribute <var> defined outside __init__"
        self.logger = logging.getLogger()
        self.request_type = None
        self.operation = None
        self.vpc_id = None
        self.region = None
        self.aws_akey = None
        self.aws_skey = None
        self.aws_token = None
        self.inst_type = None

        # AWS and PSafe connection handles
        self.ec2 = None
        # self.client = None
        self.ssm = None

        self.ec2mgr = None
        self.ssmmgr = None

    def init_vars(self, event, logger):
        """  variable initialization """
        self.logger = logger
        self.logger.info("Method Entry.")

        self.request_type = event['requestType']
        self.operation = event['operation']
        self.region = event['svcPayload'][0]['region']
        self.vpc_id = event['svcPayload'][0]['vpcId']
        self.pub_subnet_id = event['svcPayload'][0]['pubSubnetId']
        self.pkey_name = event['svcPayload'][0]['pkeyName']
        self.inst_type = event['svcPayload'][0]['instType']
        self.name_tag = event['svcPayload'][0]['nameTag']
        self.aws_akey = event['svcPayload'][0]['accessKey']
        self.aws_skey = event['svcPayload'][0]['secretKey']
        self.aws_token = event['svcPayload'][0]['sessionToken']

    # Initialization - connection to AWS initialization
    def sign_in(self):
        """ setup initial connections to aws """
        self.logger.info("Method Entry.")

        #self.ec2 = boto3.resource('ec2', region_name=self.region, aws_access_key_id=self.aws_akey,
        #                        aws_secret_access_key=self.aws_skey, aws_session_token=self.aws_token)

        self.client = boto3.client('ec2', region_name=self.region, aws_access_key_id=self.aws_akey,
                                   aws_secret_access_key=self.aws_skey, aws_session_token=self.aws_token)

        self.ssm = boto3.client('ssm', region_name=self.region, aws_access_key_id=self.aws_akey,
                                aws_secret_access_key=self.aws_skey, aws_session_token=self.aws_token)

        # setup resource handlers/managers
        self.ec2mgr = EC2Manager(self.logger, self.client, self.region)

        self.ssmmgr = SSMManager(self.logger, self.ssm, self.region)

    def validate_request(self, event):
        """
        This is do a minimal validation of request to check if expected params/values are present
        :param event: incoming payload
        :return: True/False indicating if the request params are valid or not
        """
        self.logger.info("Method Entry.")

        # lets first validate the inputs params for basic checking.
        request_type = event['requestType']
        operation = event['operation']
        if request_type not in ['ec2']:
            return False
        if operation not in ['create', 'delete']:
            return False
        return True

    # Main entry point for acting on the request
    def process_request(self, event):
        """
        Main entry point for Processing the request
        :return:
        """
        self.logger.info("Method Entry.")
        if self.validate_request(event) != True:
            return False

        return self.__process_request(event)

    def __process_request(self, event):
        """
        Private impl method for the Processing the request
        :return:
        """
        self.logger.info("Method Entry.")
        if event['requestType'] == 'ec2':
            return self.__setup_ec2(event)

        return False

    def __setup_ec2(self, event):
        self.logger.info("Method Entry.")
        if event['operation'] == 'create':
            return self.ec2mgr.create_jump_ec2(self.vpc_id, self.inst_type, self.name_tag, self.pub_subnet_id,
                                               self.pkey_name)
