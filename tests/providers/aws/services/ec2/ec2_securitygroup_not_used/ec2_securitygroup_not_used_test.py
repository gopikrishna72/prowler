from re import search
from unittest import mock

from boto3 import client, resource, session
from moto import mock_ec2

from prowler.providers.aws.lib.audit_info.models import AWS_Audit_Info

AWS_REGION = "us-east-1"
EXAMPLE_AMI_ID = "ami-12c6146b"
AWS_ACCOUNT_NUMBER = "123456789012"


class Test_ec2_securitygroup_not_used:
    def set_mocked_audit_info(self):
        audit_info = AWS_Audit_Info(
            session_config=None,
            original_session=None,
            audit_session=session.Session(
                profile_name=None,
                botocore_session=None,
            ),
            audited_account=AWS_ACCOUNT_NUMBER,
            audited_user_id=None,
            audited_partition="aws",
            audited_identity_arn=None,
            profile=None,
            profile_region=None,
            credentials=None,
            assumed_role_info=None,
            audited_regions=["us-east-1", "eu-west-1"],
            organizations_metadata=None,
            audit_resources=None,
        )

        return audit_info

    @mock_ec2
    def test_ec2_default_sgs(self):
        # Create EC2 Mocked Resources
        ec2_client = client("ec2", region_name=AWS_REGION)
        ec2_client.create_vpc(CidrBlock="10.0.0.0/16")

        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.ec2.ec2_securitygroup_not_used.ec2_securitygroup_not_used.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_securitygroup_not_used.ec2_securitygroup_not_used import (
                ec2_securitygroup_not_used,
            )

            check = ec2_securitygroup_not_used()
            result = check.execute()

            # Default sg per region are excluded
            assert len(result) == 0

    @mock_ec2
    def test_ec2_unused_sg(self):
        # Create EC2 Mocked Resources
        ec2 = resource("ec2", AWS_REGION)
        ec2_client = client("ec2", region_name=AWS_REGION)
        vpc_id = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]
        sg = ec2.create_security_group(
            GroupName="test-sg", Description="test", VpcId=vpc_id
        )

        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.ec2.ec2_securitygroup_not_used.ec2_securitygroup_not_used.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_securitygroup_not_used.ec2_securitygroup_not_used import (
                ec2_securitygroup_not_used,
            )

            check = ec2_securitygroup_not_used()
            result = check.execute()

            # One custom sg
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert search(
                "it is not being used",
                result[0].status_extended,
            )
            assert (
                result[0].resource_arn
                == f"arn:{current_audit_info.audited_partition}:ec2:{AWS_REGION}:{current_audit_info.audited_account}:security-group/{sg.id}"
            )

    @mock_ec2
    def test_ec2_used_default_sg(self):
        # Create EC2 Mocked Resources
        ec2 = resource("ec2", AWS_REGION)
        ec2_client = client("ec2", region_name=AWS_REGION)
        vpc_id = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]
        sg = ec2.create_security_group(
            GroupName="test-sg", Description="test", VpcId=vpc_id
        )
        subnet = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.0.0/18")
        subnet.create_network_interface(Groups=[sg.id])

        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.ec2.ec2_securitygroup_not_used.ec2_securitygroup_not_used.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_securitygroup_not_used.ec2_securitygroup_not_used import (
                ec2_securitygroup_not_used,
            )

            check = ec2_securitygroup_not_used()
            result = check.execute()

            # One custom sg
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert search(
                "it is being used",
                result[0].status_extended,
            )
            assert (
                result[0].resource_arn
                == f"arn:{current_audit_info.audited_partition}:ec2:{AWS_REGION}:{current_audit_info.audited_account}:security-group/{sg.id}"
            )
