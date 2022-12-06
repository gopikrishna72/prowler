from prowler.lib.check.models import Check, Check_Report
from prowler.providers.azure.services.storage.storage_client import storage_client


class storage_blob_public_access_level_is_disabled(Check):
    def execute(self) -> Check_Report:
        findings = []
        for subscription, storage_accounts in storage_client.storage_accounts.items():
            for storage_account in storage_accounts:
                report = Check_Report(self.metadata())
                report.region = storage_client.region
                report.status = "PASS"
                report.status_extended = f"Storage account {storage_account.name} from subscription {subscription} has allow blob public access disabled"
                report.resource_id = storage_account.name
                report.resource_arn = storage_account.id
                if not storage_account.allow_blob_public_access:
                    report.status = "FAIL"
                    report.status_extended = f"Storage account {storage_account.name} from subscription {subscription} has allow blob public access enabled"

                findings.append(report)

        return findings
