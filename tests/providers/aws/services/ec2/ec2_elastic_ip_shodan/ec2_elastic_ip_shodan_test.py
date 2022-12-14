from unittest import mock

from boto3 import client
from moto import mock_ec2

from prowler.config.config import get_config_var

EXAMPLE_AMI_ID = "ami-12c6146b"
shodan_api_key = get_config_var("shodan_api_key")


class Test_ec2_elastic_ip_shodan:
    if shodan_api_key:

        @mock_ec2
        def test_ec2_one_instances_no_public_ip(self):
            # Create EC2 Mocked Resources
            ec2_client = client("ec2")
            # Create EC2 Instance
            ec2_client.run_instances(ImageId=EXAMPLE_AMI_ID, MinCount=1, MaxCount=1)

            from prowler.providers.aws.lib.audit_info.audit_info import (
                current_audit_info,
            )
            from prowler.providers.aws.services.ec2.ec2_service import EC2

            current_audit_info.audited_partition = "aws"
            current_audit_info.audited_regions = ["eu-west-1", "us-east-1"]

            with mock.patch(
                "prowler.providers.aws.services.ec2.ec2_elastic_ip_shodan.ec2_elastic_ip_shodan.ec2_client",
                new=EC2(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.ec2.ec2_elastic_ip_shodan.ec2_elastic_ip_shodan import (
                    ec2_elastic_ip_shodan,
                )

                check = ec2_elastic_ip_shodan()
                result = check.execute()

                assert len(result) == 0

        @mock_ec2
        def test_ec2_one_unattached_eip(self):
            # Create EC2 Mocked Resources
            ec2_client = client("ec2")
            # Create EC2 Instance
            ec2_client.allocate_address(Domain="vpc")

            from prowler.providers.aws.lib.audit_info.audit_info import (
                current_audit_info,
            )
            from prowler.providers.aws.services.ec2.ec2_service import EC2

            current_audit_info.audited_partition = "aws"
            current_audit_info.audited_regions = ["eu-west-1", "us-east-1"]

            with mock.patch(
                "prowler.providers.aws.services.ec2.ec2_elastic_ip_shodan.ec2_elastic_ip_shodan.ec2_client",
                new=EC2(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.ec2.ec2_elastic_ip_shodan.ec2_elastic_ip_shodan import (
                    ec2_elastic_ip_shodan,
                )

                check = ec2_elastic_ip_shodan()
                result = check.execute()

                assert len(result) == 0

        @mock_ec2
        def test_ec2_one_attached_eip(self):
            # Create EC2 Mocked Resources
            ec2_client = client("ec2")
            # Create EC2 Instance
            instance = ec2_client.run_instances(
                ImageId=EXAMPLE_AMI_ID, MinCount=1, MaxCount=1
            )
            allocation = ec2_client.allocate_address(Domain="vpc")
            ec2_client.associate_address(
                AllocationId=allocation["AllocationId"],
                InstanceId=instance["Instances"][0]["InstanceId"],
            )

            from prowler.providers.aws.lib.audit_info.audit_info import (
                current_audit_info,
            )
            from prowler.providers.aws.services.ec2.ec2_service import EC2

            current_audit_info.audited_partition = "aws"
            current_audit_info.audited_regions = ["eu-west-1", "us-east-1"]

            with mock.patch(
                "prowler.providers.aws.services.ec2.ec2_elastic_ip_shodan.ec2_elastic_ip_shodan.ec2_client",
                new=EC2(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.ec2.ec2_elastic_ip_shodan.ec2_elastic_ip_shodan import (
                    ec2_elastic_ip_shodan,
                )

                check = ec2_elastic_ip_shodan()
                result = check.execute()

                assert len(result) == 1
