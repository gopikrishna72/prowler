from prowler.lib.check.models import Check, Check_Report_AWS
from prowler.providers.aws.services.cognito.cognito_idp_client import cognito_idp_client


class cognito_user_pool_password_policy_minimum_length_14(Check):
    def execute(self):
        findings = []
        for pool in cognito_idp_client.user_pools.values():
            report = Check_Report_AWS(self.metadata())
            report.region = pool.region
            report.resource_id = pool.id
            report.resource_arn = pool.arn
            report.resource_tags = pool.tags
            if pool.password_policy:
                if pool.password_policy.get("MinimumLength", 8) >= 14:
                    report.status = "PASS"
                    report.status_extended = f"User pool {pool.name} has a password policy with a minimum length of 14 characters."
                else:
                    report.status = "FAIL"
                    report.status_extended = f"User pool {pool.name} does not have a password policy with a minimum length of 14 characters."
            else:
                report.status = "FAIL"
                report.status_extended = (
                    f"User pool {pool.name} has not a password policy set."
                )
            findings.append(report)

        return findings
