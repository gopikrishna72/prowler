from prowler.lib.check.models import Check, Check_Report_Azure
from prowler.providers.azure.services.monitor.monitor_client import monitor_client


class monitor_alert_delete_sqlserver_fr(Check):
    def execute(self) -> Check_Report_Azure:
        findings = []

        for (
            subscription_name,
            activity_log_alerts,
        ) in monitor_client.alert_rules.items():
            report = Check_Report_Azure(self.metadata())
            report.status = "FAIL"
            report.subscription = subscription_name
            report.resource_name = "Monitor"
            report.resource_id = "Monitor"
            report.status_extended = f"There is not an alert for Delete SQL Server Firewall Rule in subscription {subscription_name}."
            for alert_rule in activity_log_alerts:
                if (
                    alert_rule.condition.all_of[1].equals
                    == "Microsoft.Sql/servers/firewallRules/delete"
                    and alert_rule.enabled
                ):
                    report.status = "PASS"
                    report.status_extended = f"Alert {alert_rule.name} is configured to trigger when a fireall rule for SQL Server is deleted in subscription {subscription_name}."
                    report.resource_name = alert_rule.name
                    report.resource_id = alert_rule.id
                    report.subscription = subscription_name
                    break

            findings.append(report)

        return findings
