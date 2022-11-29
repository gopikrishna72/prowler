from lib.check.models import Check, Check_Report
from providers.azure.services.storage.storage_client import storage_client


class storage_ensure_encryption_with_customer_managed_keys(Check):
    def execute(self) -> Check_Report:
        findings = []
        for subscription, storage_accounts in storage_client.storage_accounts.items():
            for storage_account in storage_accounts:
                report = Check_Report(self.metadata())
                report.region = storage_client.region
                report.status = "PASS"
                report.status_extended = f"Storage account {storage_account.name} from subscription {subscription} encrypts with CMKs"
                report.resource_id = storage_account.name
                report.resource_arn = storage_account.id
                if storage_account.encryption_type != "Microsoft.Keyvault":
                    report.status = "FAIL"
                    report.status_extended = f"Storage account {storage_account.name} from subscription {subscription} does not encrypt with CMKs"

                findings.append(report)

        return findings
