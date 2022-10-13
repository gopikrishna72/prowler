from lib.check.models import Check, Check_Report
from providers.aws.services.iam.iam_client import iam_client


class iam_support_role_created(Check):
    def execute(self) -> Check_Report:
        findings = []
        report = Check_Report(self.metadata)
        report.region = iam_client.region
        report.resource_id = (
            "arn:aws:iam::aws:policy/aws-service-role/AWSSupportServiceRolePolicy"
        )
        if iam_client.support_roles:
            report.status = "PASS"
            report.status_extended = f"Support policy attached to role {iam_client.support_roles[0]['RoleName']}"
        else:
            report.status = "FAIL"
            report.status_extended = f"Support policy is not attached to any role"
        findings.append(report)
        return findings
