from re import search
from unittest import mock

from boto3 import client, resource
from moto import mock_ec2, mock_elbv2

from tests.providers.aws.audit_info_utils import (
    AWS_REGION_EU_WEST_1,
    set_mocked_aws_audit_info,
)

AWS_REGION = "eu-west-1"
AWS_ACCOUNT_NUMBER = "123456789012"


class Test_elbv2_deletion_protection:
    @mock_elbv2
    def test_elb_no_balancers(self):
        from prowler.providers.aws.services.elbv2.elbv2_service import ELBv2

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1]),
        ), mock.patch(
            "prowler.providers.aws.services.elbv2.elbv2_deletion_protection.elbv2_deletion_protection.elbv2_client",
            new=ELBv2(set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])),
        ):
            # Test Check
            from prowler.providers.aws.services.elbv2.elbv2_deletion_protection.elbv2_deletion_protection import (
                elbv2_deletion_protection,
            )

            check = elbv2_deletion_protection()
            result = check.execute()

            assert len(result) == 0

    @mock_ec2
    @mock_elbv2
    def test_elbv2_without_deletion_protection(self):
        conn = client("elbv2", region_name=AWS_REGION)
        ec2 = resource("ec2", region_name=AWS_REGION)

        security_group = ec2.create_security_group(
            GroupName="a-security-group", Description="First One"
        )
        vpc = ec2.create_vpc(CidrBlock="172.28.7.0/24", InstanceTenancy="default")
        subnet1 = ec2.create_subnet(
            VpcId=vpc.id, CidrBlock="172.28.7.192/26", AvailabilityZone=f"{AWS_REGION}a"
        )
        subnet2 = ec2.create_subnet(
            VpcId=vpc.id, CidrBlock="172.28.7.0/26", AvailabilityZone=f"{AWS_REGION}b"
        )

        lb = conn.create_load_balancer(
            Name="my-lb",
            Subnets=[subnet1.id, subnet2.id],
            SecurityGroups=[security_group.id],
            Scheme="internal",
            Type="application",
        )["LoadBalancers"][0]

        conn.modify_load_balancer_attributes(
            LoadBalancerArn=lb["LoadBalancerArn"],
            Attributes=[
                {"Key": "deletion_protection.enabled", "Value": "false"},
            ],
        )

        from prowler.providers.aws.services.elbv2.elbv2_service import ELBv2

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1]),
        ), mock.patch(
            "prowler.providers.aws.services.elbv2.elbv2_deletion_protection.elbv2_deletion_protection.elbv2_client",
            new=ELBv2(set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])),
        ):
            from prowler.providers.aws.services.elbv2.elbv2_deletion_protection.elbv2_deletion_protection import (
                elbv2_deletion_protection,
            )

            check = elbv2_deletion_protection()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert search(
                "does not have deletion protection",
                result[0].status_extended,
            )
            assert result[0].resource_id == "my-lb"
            assert result[0].resource_arn == lb["LoadBalancerArn"]

    @mock_ec2
    @mock_elbv2
    def test_elbv2_with_deletion_protection(self):
        conn = client("elbv2", region_name=AWS_REGION)
        ec2 = resource("ec2", region_name=AWS_REGION)

        security_group = ec2.create_security_group(
            GroupName="a-security-group", Description="First One"
        )
        vpc = ec2.create_vpc(CidrBlock="172.28.7.0/24", InstanceTenancy="default")
        subnet1 = ec2.create_subnet(
            VpcId=vpc.id, CidrBlock="172.28.7.192/26", AvailabilityZone=f"{AWS_REGION}a"
        )
        subnet2 = ec2.create_subnet(
            VpcId=vpc.id, CidrBlock="172.28.7.0/26", AvailabilityZone=f"{AWS_REGION}b"
        )

        lb = conn.create_load_balancer(
            Name="my-lb",
            Subnets=[subnet1.id, subnet2.id],
            SecurityGroups=[security_group.id],
            Scheme="internal",
        )["LoadBalancers"][0]

        conn.modify_load_balancer_attributes(
            LoadBalancerArn=lb["LoadBalancerArn"],
            Attributes=[
                {"Key": "deletion_protection.enabled", "Value": "true"},
            ],
        )

        from prowler.providers.aws.services.elbv2.elbv2_service import ELBv2

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1]),
        ), mock.patch(
            "prowler.providers.aws.services.elbv2.elbv2_deletion_protection.elbv2_deletion_protection.elbv2_client",
            new=ELBv2(set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])),
        ):
            from prowler.providers.aws.services.elbv2.elbv2_deletion_protection.elbv2_deletion_protection import (
                elbv2_deletion_protection,
            )

            check = elbv2_deletion_protection()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "PASS"
            assert search(
                "has deletion protection enabled",
                result[0].status_extended,
            )
            assert result[0].resource_id == "my-lb"
            assert result[0].resource_arn == lb["LoadBalancerArn"]
