from lib.check.models import Check, Check_Report
from providers.aws.services.iam.iam_client import iam_client


class cloudwatch_cross_account_sharing_disabled(Check):
    def execute(self):
        findings = []
        report = Check_Report(self.metadata)
        report.status = "PASS"
        report.status_extended = "CloudWatch doesn't allows cross-account sharing"
        report.resource_id = "CloudWatch-CrossAccountSharingRole"
        report.region = iam_client.region
        for role in iam_client.roles:
            if role["RoleName"] == "CloudWatch-CrossAccountSharingRole":
                report.resource_arn = role["Arn"]
                report.status = "FAIL"
                report.status_extended = "CloudWatch has allowed cross-account sharing."
        findings.append(report)
        return findings
