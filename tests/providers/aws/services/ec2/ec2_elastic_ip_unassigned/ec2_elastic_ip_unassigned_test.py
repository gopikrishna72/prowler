from re import search
from unittest import mock

from boto3 import client, resource
from moto import mock_ec2

from tests.providers.aws.audit_info_utils import (
    AWS_REGION_EU_WEST_1,
    set_mocked_aws_audit_info,
)

AWS_REGION = "us-east-1"
EXAMPLE_AMI_ID = "ami-12c6146b"
AWS_ACCOUNT_NUMBER = "123456789012"


class Test_ec2_elastic_ip_unassigned:
    @mock_ec2
    def test_no_eips(self):
        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.ec2.ec2_elastic_ip_unassigned.ec2_elastic_ip_unassigned.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_elastic_ip_unassigned.ec2_elastic_ip_unassigned import (
                ec2_elastic_ip_unassigned,
            )

            check = ec2_elastic_ip_unassigned()
            result = check.execute()

            assert len(result) == 0

    @mock_ec2
    def test_eip_unassociated(self):
        # Create EC2 Mocked Resources
        ec2_client = client("ec2", region_name=AWS_REGION)
        allocation_id = ec2_client.allocate_address(
            Domain="vpc", Address="127.38.43.222"
        )["AllocationId"]

        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.ec2.ec2_elastic_ip_unassigned.ec2_elastic_ip_unassigned.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_elastic_ip_unassigned.ec2_elastic_ip_unassigned import (
                ec2_elastic_ip_unassigned,
            )

            check = ec2_elastic_ip_unassigned()
            results = check.execute()

            assert len(results) == 1
            assert results[0].status == "FAIL"
            assert results[0].region == AWS_REGION
            assert results[0].resource_tags == []
            assert search(
                "is not associated",
                results[0].status_extended,
            )
            assert (
                results[0].resource_arn
                == f"arn:{current_audit_info.audited_partition}:ec2:{AWS_REGION}:{current_audit_info.audited_account}:eip-allocation/{allocation_id}"
            )

    @mock_ec2
    def test_eip_associated(self):
        # Create EC2 Mocked Resources
        ec2_client = client("ec2", region_name=AWS_REGION)
        ec2_resource = resource("ec2", region_name=AWS_REGION)

        reservation = ec2_client.run_instances(
            ImageId=EXAMPLE_AMI_ID, MinCount=1, MaxCount=1
        )
        instance = ec2_resource.Instance(reservation["Instances"][0]["InstanceId"])

        eip = ec2_client.allocate_address(Domain="vpc")

        eip = ec2_resource.VpcAddress(eip["AllocationId"])

        ec2_client.associate_address(
            InstanceId=instance.id, AllocationId=eip.allocation_id
        )

        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.ec2.ec2_elastic_ip_unassigned.ec2_elastic_ip_unassigned.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_elastic_ip_unassigned.ec2_elastic_ip_unassigned import (
                ec2_elastic_ip_unassigned,
            )

            check = ec2_elastic_ip_unassigned()
            results = check.execute()

            assert len(results) == 1
            assert results[0].status == "PASS"
            assert results[0].region == AWS_REGION
            assert results[0].resource_tags == []
            assert search(
                "is associated",
                results[0].status_extended,
            )
            assert (
                results[0].resource_arn
                == f"arn:{current_audit_info.audited_partition}:ec2:{AWS_REGION}:{current_audit_info.audited_account}:eip-allocation/{eip.allocation_id}"
            )
