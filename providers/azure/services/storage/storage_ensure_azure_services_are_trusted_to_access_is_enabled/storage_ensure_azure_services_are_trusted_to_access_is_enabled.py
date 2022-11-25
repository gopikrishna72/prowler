from lib.check.models import Check, Check_Report
from providers.azure.services.storage.storage_client import storage_client


class storage_ensure_azure_services_are_trusted_to_access_is_enabled(Check):
    def execute(self) -> Check_Report:
        findings = []
        for subscription, storage_accounts in storage_client.storage_accounts.items():
            for storage_account in storage_accounts:
                report = Check_Report(self.metadata)
                report.region = storage_client.region
                report.status = "PASS"
                report.status_extended = f"Storage account {storage_account.name} from subscription {subscription} allows trusted Microsoft services to access this storage account"
                report.resource_id = storage_account.name
                report.resource_arn = storage_account.id
                if "AzureServices" not in storage_account.network_rule_set.bypass:
                    report.status = "FAIL"
                    report.status_extended = f"Storage account {storage_account.name} from subscription {subscription} does not allow trusted Microsoft services to access this storage account"

                findings.append(report)

        return findings
