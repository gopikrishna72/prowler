from re import search
from unittest import mock

from boto3 import client, session
from moto import mock_s3

from prowler.providers.aws.lib.audit_info.models import AWS_Audit_Info

AWS_ACCOUNT_NUMBER = "123456789012"
AWS_REGION = "us-east-1"


class Test_s3_bucket_policy_public_write_access:
    # Mocked Audit Info
    def set_mocked_audit_info(self):
        audit_info = AWS_Audit_Info(
            session_config=None,
            original_session=None,
            audit_session=session.Session(
                profile_name=None,
                botocore_session=None,
                region_name=AWS_REGION,
            ),
            audited_account=AWS_ACCOUNT_NUMBER,
            audited_user_id=None,
            audited_partition="aws",
            audited_identity_arn=None,
            profile=None,
            profile_region=AWS_REGION,
            credentials=None,
            assumed_role_info=None,
            audited_regions=None,
            organizations_metadata=None,
            audit_resources=None,
        )
        return audit_info

    @mock_s3
    def test_bucket_no_policy(self):
        s3_client_us_east_1 = client("s3", region_name="us-east-1")
        bucket_name_us = "bucket_test_us"
        s3_client_us_east_1.create_bucket(Bucket=bucket_name_us)

        from prowler.providers.aws.services.s3.s3_service import S3

        audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.s3.s3_bucket_policy_public_write_access.s3_bucket_policy_public_write_access.s3_client",
                new=S3(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.s3.s3_bucket_policy_public_write_access.s3_bucket_policy_public_write_access import (
                    s3_bucket_policy_public_write_access,
                )

                check = s3_bucket_policy_public_write_access()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "PASS"
                assert search(
                    "does not have a bucket policy",
                    result[0].status_extended,
                )
                assert result[0].resource_id == bucket_name_us
                assert (
                    result[0].resource_arn
                    == f"arn:{audit_info.audited_partition}:s3:::{bucket_name_us}"
                )
                assert result[0].region == "us-east-1"

    @mock_s3
    def test_bucket_comply_policy(self):
        s3_client_us_east_1 = client("s3", region_name="us-east-1")
        bucket_name_us = "bucket_test_us"
        s3_client_us_east_1.create_bucket(
            Bucket=bucket_name_us, ObjectOwnership="BucketOwnerEnforced"
        )

        encryption_policy = '{"Version": "2012-10-17","Id": "PutObjPolicy","Statement": [{"Sid": "DenyIncorrectEncryptionHeader","Effect": "Deny","Principal": "*","Action": "s3:PutObject","Resource": "arn:aws:s3:::bucket_test_us/*","Condition": {"StringNotEquals": {"s3:x-amz-server-side-encryption": "aws:kms"}}}]}'
        s3_client_us_east_1.put_bucket_policy(
            Bucket=bucket_name_us,
            Policy=encryption_policy,
        )
        from prowler.providers.aws.services.s3.s3_service import S3

        audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.s3.s3_bucket_policy_public_write_access.s3_bucket_policy_public_write_access.s3_client",
                new=S3(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.s3.s3_bucket_policy_public_write_access.s3_bucket_policy_public_write_access import (
                    s3_bucket_policy_public_write_access,
                )

                check = s3_bucket_policy_public_write_access()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "PASS"
                assert search(
                    "does not allow public write access in the bucket policy",
                    result[0].status_extended,
                )
                assert result[0].resource_id == bucket_name_us
                assert (
                    result[0].resource_arn
                    == f"arn:{audit_info.audited_partition}:s3:::{bucket_name_us}"
                )
                assert result[0].region == "us-east-1"

    @mock_s3
    def test_bucket_public_write_policy(self):
        s3_client_us_east_1 = client("s3", region_name="us-east-1")
        bucket_name_us = "bucket_test_us"
        s3_client_us_east_1.create_bucket(
            Bucket=bucket_name_us, ObjectOwnership="BucketOwnerEnforced"
        )
        public_write_policy = '{"Version": "2012-10-17","Id": "PutObjPolicy","Statement": [{"Sid": "PublicWritePolicy","Effect": "Allow","Principal": "*","Action": "s3:PutObject","Resource": "arn:aws:s3:::bucket_test_us/*"}]}'
        s3_client_us_east_1.put_bucket_policy(
            Bucket=bucket_name_us,
            Policy=public_write_policy,
        )
        from prowler.providers.aws.services.s3.s3_service import S3

        audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.s3.s3_bucket_policy_public_write_access.s3_bucket_policy_public_write_access.s3_client",
                new=S3(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.s3.s3_bucket_policy_public_write_access.s3_bucket_policy_public_write_access import (
                    s3_bucket_policy_public_write_access,
                )

                check = s3_bucket_policy_public_write_access()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "FAIL"
                assert search(
                    "allows public write access in the bucket policy",
                    result[0].status_extended,
                )
                assert result[0].resource_id == bucket_name_us
                assert (
                    result[0].resource_arn
                    == f"arn:{audit_info.audited_partition}:s3:::{bucket_name_us}"
                )
                assert result[0].region == "us-east-1"
