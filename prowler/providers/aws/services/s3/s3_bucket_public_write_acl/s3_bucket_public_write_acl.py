from prowler.lib.check.models import Check, Check_Report_AWS
from prowler.providers.aws.services.s3.s3_client import s3_client
from prowler.providers.aws.services.s3.s3control_client import s3control_client


class s3_bucket_public_write_acl(Check):
    def execute(self):
        findings = []
        # 1. Check if public buckets are restricted at account level
        if (
            s3control_client.account_public_access_block
            and s3control_client.account_public_access_block.ignore_public_acls
            and s3control_client.account_public_access_block.restrict_public_buckets
        ):
            report = Check_Report_AWS(self.metadata())
            report.status = "PASS"
            report.status_extended = "All S3 public access blocked at account level."
            report.region = s3control_client.region
            report.resource_id = s3_client.audited_account
            report.resource_arn = s3_client.audited_account_arn
            findings.append(report)
        else:
            # 2. If public access is not blocked at account level, check it at each bucket level
            for bucket in s3_client.buckets:
                if bucket.public_access_block:
                    report = Check_Report_AWS(self.metadata())
                    report.region = bucket.region
                    report.resource_id = bucket.name
                    report.resource_arn = bucket.arn
                    report.resource_tags = bucket.tags
                    report.status = "PASS"
                    report.status_extended = f"S3 Bucket {bucket.name} is not publicly writable."
                    if not (
                        bucket.public_access_block.ignore_public_acls
                        and bucket.public_access_block.restrict_public_buckets
                    ):
                        # 3. If bucket has no public block, check bucket ACL
                        for grantee in bucket.acl_grantees:
                            if grantee.type in "Group":
                                if (
                                    "AllUsers" in grantee.URI
                                    or "AuthenticatedUsers" in grantee.URI
                                ) and (
                                    grantee.permission == "FULL_CONTROL" or
                                    grantee.permission == "WRITE" or
                                    grantee.permission == "WRITE_ACL"
                                ):
                                    report.status = "FAIL"
                                    report.status_extended = f"S3 Bucket {bucket.name} writable by anyone due to bucket ACL: {grantee.URI.split('/')[-1]} having {grantee.permission}"


                    findings.append(report)
        return findings
