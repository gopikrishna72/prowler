from re import search
from unittest import mock

from boto3 import client, resource
from moto import mock_ec2, mock_elb

AWS_REGION = "eu-west-1"
AWS_ACCOUNT_NUMBER = "123456789012"


class Test_elb_request_smugling:
    @mock_elb
    def test_elb_no_balancers(self):

        from providers.aws.lib.audit_info.audit_info import current_audit_info
        from providers.aws.services.elb.elb_service import ELB

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "providers.aws.services.elb.elb_internet_facing.elb_internet_facing.elb_client",
            new=ELB(current_audit_info),
        ):
            # Test Check
            from providers.aws.services.elb.elb_internet_facing.elb_internet_facing import (
                elb_internet_facing,
            )

            check = elb_internet_facing()
            result = check.execute()

            assert len(result) == 0

    @mock_ec2
    @mock_elb
    def test_elb_private(self):
        elb = client("elb", region_name=AWS_REGION)
        ec2 = resource("ec2", region_name=AWS_REGION)

        security_group = ec2.create_security_group(
            GroupName="sg01", Description="Test security group sg01"
        )

        elb.create_load_balancer(
            LoadBalancerName="my-lb",
            Listeners=[
                {"Protocol": "tcp", "LoadBalancerPort": 80, "InstancePort": 8080},
                {"Protocol": "http", "LoadBalancerPort": 81, "InstancePort": 9000},
            ],
            AvailabilityZones=[f"{AWS_REGION}a"],
            Scheme="internal",
            SecurityGroups=[security_group.id],
        )

        from providers.aws.lib.audit_info.audit_info import current_audit_info
        from providers.aws.services.elb.elb_service import ELB

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "providers.aws.services.elb.elb_internet_facing.elb_internet_facing.elb_client",
            new=ELB(current_audit_info),
        ):
            from providers.aws.services.elb.elb_internet_facing.elb_internet_facing import (
                elb_internet_facing,
            )

            check = elb_internet_facing()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "PASS"
            assert search(
                "is not internet facing",
                result[0].status_extended,
            )
            assert result[0].resource_id == "my-lb"

    @mock_ec2
    @mock_elb
    def test_elb_with_deletion_protection(self):
        elb = client("elb", region_name=AWS_REGION)
        ec2 = resource("ec2", region_name=AWS_REGION)

        security_group = ec2.create_security_group(
            GroupName="sg01", Description="Test security group sg01"
        )

        elb.create_load_balancer(
            LoadBalancerName="my-lb",
            Listeners=[
                {"Protocol": "tcp", "LoadBalancerPort": 80, "InstancePort": 8080},
                {"Protocol": "http", "LoadBalancerPort": 81, "InstancePort": 9000},
            ],
            AvailabilityZones=[f"{AWS_REGION}a"],
            Scheme="internet-facing",
            SecurityGroups=[security_group.id],
        )

        from providers.aws.lib.audit_info.audit_info import current_audit_info
        from providers.aws.services.elb.elb_service import ELB

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "providers.aws.services.elb.elb_internet_facing.elb_internet_facing.elb_client",
            new=ELB(current_audit_info),
        ):
            from providers.aws.services.elb.elb_internet_facing.elb_internet_facing import (
                elb_internet_facing,
            )

            check = elb_internet_facing()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert search(
                "is internet facing",
                result[0].status_extended,
            )
            assert result[0].resource_id == "my-lb"
