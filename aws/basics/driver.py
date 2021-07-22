import logging
import sys

import awsdriver

"""
This is a test driver code to be used for local testing
"""


class TestDriver:
    def __init__(self):
        print("TestDriver _init_")
        loglevel = logging.INFO
        # logging.basicConfig(stream=sys.stdout, format='%(levelname)s:%(module)s:%(funcName)s:%(message)s',
        #   level=driver.args_loglevel)
        # logging.info('test_driver main')
        logging.basicConfig(stream=sys.stdout,
                            format='%(levelname)s:%(module)s::%(funcName)s:%(message)s',
                            level=loglevel)
        self.logger = logging.getLogger()

    # Valid values of:
    # requestType: "ec2"  # in future to add other services
    # accessType: "basic", "elevated", "close" [close is available only for update]
    def prepare_payload(self):
        payload = {
          "requestType": "ec2",
          "operation": "create",
          "logLevel": "info",
          "svcPayload": [
            {
              "region": "us-west-2",
              "vpcId": "vpc-02844162dd48a3c3f",
              "pubSubnetId": "subnet-07d183c3d2677b162",  # we could introspect this from VPC, but taking it as arg to make the code simple
              "pkeyName": "vasu-glue-key",  # we could create keypair on the fly, but taking it as arg, so user can connect via ssh
              "instType": "t2.micro",
              "nameTag": "vasu-test",
              "accessKey": "",
              "secretKey": "",
              "sessionToken": ""
            }
          ]
        }
        return payload

    def do_start(self):
        event = driver.prepare_payload()

        aws_driver = awsdriver.AWSDriver()
        aws_driver.init_vars(event, self.logger)
        aws_driver.sign_in()

        request_type = event['requestType']
        operation = event['operation']
        print(">>>> requestType: ", request_type, " and operation", operation)

        if not aws_driver.process_request(event):
            self.logger.error("Unable to process the Request. Check Payload.")


# main entry point for the Driver
if __name__ == "__main__":
    driver = TestDriver()
    driver.do_start()
    # driver.temp_test_local()
