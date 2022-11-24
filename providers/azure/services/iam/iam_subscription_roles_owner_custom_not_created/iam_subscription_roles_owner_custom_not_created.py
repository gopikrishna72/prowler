from re import search

from lib.check.models import Check, Check_Report
from providers.azure.services.iam.iam_client import iam_client


class iam_subscription_roles_owner_custom_not_created(Check):
    def execute(self) -> Check_Report:
        findings = []
        for swubscription, role in iam_client.roles.items():
            report = Check_Report(self.metadata)
            report.region = iam_client.region
            report.status = "PASS"
            report.status_extended = f"Role {role.name} from subscription {swubscription} is not a custom owner role"
            for scope in role.assignable_scopes:
                if search("^/.*", scope):
                    for permission_item in role.permissions:
                        for action in permission_item.actions:
                            if action == "*":
                                report.status = "FAIL"
                                report.status_extended = f"Role {role.name} from subscription {swubscription} is a custom owner role"
                                break

            findings.append(report)
        return findings
