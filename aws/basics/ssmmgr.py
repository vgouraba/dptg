import logging
import json
import boto3


class SSMManager:
    """
        The Class that handles the aspects of SystemManager
        This is just included to demonstrate the usage of multiple AWS resources/clients
    """

    def __init__(self, logger, ssm, region):
        # Placeholder for the variables. Actual assignment happens in the init_vars method
        # This is to eliminate the warning: "Instance attribute <var> defined outside __init__"
        self.logger = logger
        self.ssm = ssm
        self.region = region
