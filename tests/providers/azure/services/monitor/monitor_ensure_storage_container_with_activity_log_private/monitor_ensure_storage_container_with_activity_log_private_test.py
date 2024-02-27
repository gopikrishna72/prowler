from unittest import mock

from prowler.providers.azure.services.monitor.monitor_service import DiagnosticSetting
from prowler.providers.azure.services.storage.storage_service import Account
from tests.providers.azure.azure_fixtures import AZURE_SUBSCRIPTION


class Test_monitor_ensure_storage_container_with_activity_log_private:
    def test_monitor_ensure_storage_container_with_activity_log_private_no_subscriptions(
        self,
    ):
        monitor_client = mock.MagicMock
        monitor_client.diagnostics_settings = {}

        with mock.patch(
            "prowler.providers.azure.services.monitor.monitor_ensure_storage_container_with_activity_log_private.monitor_ensure_storage_container_with_activity_log_private.monitor_client",
            new=monitor_client,
        ):
            from prowler.providers.azure.services.monitor.monitor_ensure_storage_container_with_activity_log_private.monitor_ensure_storage_container_with_activity_log_private import (
                monitor_ensure_storage_container_with_activity_log_private,
            )

            check = monitor_ensure_storage_container_with_activity_log_private()
            result = check.execute()
            assert len(result) == 0

    def test_no_diagnostic_settings(self):
        monitor_client = mock.MagicMock
        monitor_client.diagnostics_settings = {AZURE_SUBSCRIPTION: []}
        with mock.patch(
            "prowler.providers.azure.services.monitor.monitor_ensure_storage_container_with_activity_log_private.monitor_ensure_storage_container_with_activity_log_private.monitor_client",
            new=monitor_client,
        ):
            from prowler.providers.azure.services.monitor.monitor_ensure_storage_container_with_activity_log_private.monitor_ensure_storage_container_with_activity_log_private import (
                monitor_ensure_storage_container_with_activity_log_private,
            )

            check = monitor_ensure_storage_container_with_activity_log_private()
            result = check.execute()
            assert len(result) == 1
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].status == "PASS"
            assert result[0].resource_id == "Monitor"
            assert result[0].resource_name == "Monitor"
            assert (
                result[0].status_extended
                == f"Blob public access disabled in storage account storing activity log in subscription {AZURE_SUBSCRIPTION} or not necessary."
            )

    def test_diagnostic_settings_configured(self):
        monitor_client = mock.MagicMock
        storage_client = mock.MagicMock
        monitor_client.diagnostics_settings = {
            AZURE_SUBSCRIPTION: [
                DiagnosticSetting(
                    id="id",
                    logs=[
                        mock.MagicMock(category="Administrative", enabled=True),
                        mock.MagicMock(category="Security", enabled=True),
                        mock.MagicMock(category="ServiceHealth", enabled=False),
                        mock.MagicMock(category="Alert", enabled=True),
                        mock.MagicMock(category="Recommendation", enabled=False),
                        mock.MagicMock(category="Policy", enabled=True),
                        mock.MagicMock(category="Autoscale", enabled=False),
                    ],
                    storage_account_id="/subscriptions/1234a5-123a-123a-123a-1234567890ab/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/storageaccountname1",
                ),
                DiagnosticSetting(
                    id="id2",
                    logs=[
                        mock.MagicMock(category="Administrative", enabled=True),
                        mock.MagicMock(category="Security", enabled=True),
                        mock.MagicMock(category="ServiceHealth", enabled=False),
                        mock.MagicMock(category="Alert", enabled=True),
                        mock.MagicMock(category="Recommendation", enabled=False),
                        mock.MagicMock(category="Policy", enabled=True),
                        mock.MagicMock(category="Autoscale", enabled=False),
                    ],
                    storage_account_id="/subscriptions/1224a5-123a-123a-123a-1234567890ab/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/storageaccountname2",
                ),
            ]
        }
        storage_client.storage_accounts = {
            AZURE_SUBSCRIPTION: [
                Account(
                    id="/subscriptions/1234a5-123a-123a-123a-1234567890ab/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/storageaccountname1",
                    name="storageaccountname1",
                    resouce_group_name="rg",
                    enable_https_traffic_only=True,
                    infrastructure_encryption="Enabled",
                    allow_blob_public_access=True,
                    network_rule_set="AllowAll",
                    encryption_type="Microsoft.Storage",
                    minimum_tls_version="TLS1_2",
                    private_endpoint_connections=[],
                    key_expiration_period_in_days=365,
                    blob_properties=mock.MagicMock(
                        id="id",
                        name="name",
                        type="type",
                        default_service_version="default_service_version",
                        container_delete_retention_policy="container_delete_retention_policy",
                    ),
                ),
                Account(
                    id="/subscriptions/1224a5-123a-123a-123a-1234567890ab/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/storageaccountname2",
                    name="storageaccountname2",
                    resouce_group_name="rg",
                    enable_https_traffic_only=False,
                    infrastructure_encryption="Enabled",
                    allow_blob_public_access=True,
                    network_rule_set="AllowAll",
                    encryption_type="Microsoft.Storage",
                    minimum_tls_version="TLS1_2",
                    private_endpoint_connections=[],
                    key_expiration_period_in_days=365,
                    blob_properties=mock.MagicMock(
                        id="id",
                        name="name",
                        type="type",
                        default_service_version="default_service_version",
                        container_delete_retention_policy="container_delete_retention_policy",
                    ),
                ),
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.monitor.monitor_ensure_storage_container_with_activity_log_private.monitor_ensure_storage_container_with_activity_log_private.monitor_client",
            new=monitor_client,
        ):
            with mock.patch(
                "prowler.providers.azure.services.monitor.monitor_ensure_storage_container_with_activity_log_private.monitor_ensure_storage_container_with_activity_log_private.storage_client",
                new=storage_client,
            ):
                from prowler.providers.azure.services.monitor.monitor_ensure_storage_container_with_activity_log_private.monitor_ensure_storage_container_with_activity_log_private import (
                    monitor_ensure_storage_container_with_activity_log_private,
                )

                check = monitor_ensure_storage_container_with_activity_log_private()
                result = check.execute()
                assert len(result) == 1
                assert result[0].subscription == AZURE_SUBSCRIPTION
                assert result[0].status == "FAIL"
                assert result[0].resource_id == "Monitor"
                assert result[0].resource_name == "Monitor"
                assert (
                    result[0].status_extended
                    == f"Blob public access enabled in storage account storing activity log in subscription {AZURE_SUBSCRIPTION}."
                )
