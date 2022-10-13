from json import dumps
from unittest import mock

from boto3 import client
from moto import mock_iam

from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.iam.iam_service import IAM


class Test_iam_support_role_created:
    @mock_iam
    def test_support_role_created(self):
        iam_client = client("iam")
        role_name = "test_support"
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": {
                "Sid": "test",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "sts:AssumeRole",
            },
        }
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=dumps(assume_role_policy_document),
        )
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/aws-service-role/AWSSupportServiceRolePolicy",
        )
        with mock.patch(
            "providers.aws.services.iam.iam_support_role_created.iam_support_role_created.iam_client",
            new=IAM(current_audit_info),
        ):
            from providers.aws.services.iam.iam_support_role_created.iam_support_role_created import (
                iam_support_role_created,
            )

            check = iam_support_role_created()
            result = check.execute()
            assert result[0].status == "PASS"
