from unittest import mock
from uuid import uuid4

from azure.mgmt.sql.models import (
    ServerVulnerabilityAssessment,
    VulnerabilityAssessmentRecurringScansProperties,
)

from prowler.providers.azure.services.sqlserver.sqlserver_service import Server

AZURE_SUBSCRIPTION = str(uuid4())


class Test_sqlserver_periodic_recurring_scans_enabled:
    def test_no_sql_servers(self):
        sqlserver_client = mock.MagicMock
        sqlserver_client.sql_servers = {}

        with mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled import (
                sqlserver_periodic_recurring_scans_enabled,
            )

            check = sqlserver_periodic_recurring_scans_enabled()
            result = check.execute()
            assert len(result) == 0

    def test_sql_servers_no_vulnerability_assessment(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=None,
                    encryption_protector=None,
                    vulnerability_assessment=None,
                )
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled import (
                sqlserver_periodic_recurring_scans_enabled,
            )

            check = sqlserver_periodic_recurring_scans_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"SQL Server {sql_server_name} from subscription {AZURE_SUBSCRIPTION} has vulnerability assessment disabled."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == sql_server_name
            assert result[0].resource_id == sql_server_id

    def test_sql_servers_no_vulnerability_assessment_storage_container_path(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=None,
                    encryption_protector=None,
                    vulnerability_assessment=ServerVulnerabilityAssessment(
                        storage_container_path=None
                    ),
                )
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled import (
                sqlserver_periodic_recurring_scans_enabled,
            )

            check = sqlserver_periodic_recurring_scans_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"SQL Server {sql_server_name} from subscription {AZURE_SUBSCRIPTION} has vulnerability assessment disabled."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == sql_server_name
            assert result[0].resource_id == sql_server_id

    def test_sql_servers_vulnerability_assessment_recuring_scans_disabled(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=None,
                    encryption_protector=None,
                    vulnerability_assessment=ServerVulnerabilityAssessment(
                        storage_container_path="/subcription_id/resource_group/sql_server",
                        recurring_scans=VulnerabilityAssessmentRecurringScansProperties(
                            is_enabled=False
                        ),
                    ),
                )
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled import (
                sqlserver_periodic_recurring_scans_enabled,
            )

            check = sqlserver_periodic_recurring_scans_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"SQL Server {sql_server_name} from subscription {AZURE_SUBSCRIPTION} has vulnerability assessment enabled but no recurring scans."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == sql_server_name
            assert result[0].resource_id == sql_server_id

    def test_sql_servers_vulnerability_assessment_recuring_scans_enabled(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=None,
                    encryption_protector=None,
                    vulnerability_assessment=ServerVulnerabilityAssessment(
                        storage_container_path="/subcription_id/resource_group/sql_server",
                        recurring_scans=VulnerabilityAssessmentRecurringScansProperties(
                            is_enabled=True
                        ),
                    ),
                )
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_periodic_recurring_scans_enabled.sqlserver_periodic_recurring_scans_enabled import (
                sqlserver_periodic_recurring_scans_enabled,
            )

            check = sqlserver_periodic_recurring_scans_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"SQL Server {sql_server_name} from subscription {AZURE_SUBSCRIPTION} has periodic recurring scans enabled."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == sql_server_name
            assert result[0].resource_id == sql_server_id
