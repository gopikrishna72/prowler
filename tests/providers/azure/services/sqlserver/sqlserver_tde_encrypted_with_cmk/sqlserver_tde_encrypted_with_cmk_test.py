from unittest import mock
from uuid import uuid4

from azure.mgmt.sql.models import EncryptionProtector, TransparentDataEncryption

from prowler.providers.azure.services.sqlserver.sqlserver_service import (
    Database,
    Server,
)
from tests.providers.azure.azure_fixtures import (
    AZURE_SUBSCRIPTION_ID,
    set_mocked_azure_provider,
)


class Test_sqlserver_tde_encrypted_with_cmk:
    def test_no_sql_servers(self):
        sqlserver_client = mock.MagicMock
        sqlserver_client.sql_servers = {}

        with mock.patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_azure_provider(),
        ), mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk import (
                sqlserver_tde_encrypted_with_cmk,
            )

            check = sqlserver_tde_encrypted_with_cmk()
            result = check.execute()
            assert len(result) == 0

    def test_no_sql_servers_databases(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION_ID: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=None,
                    location="location",
                )
            ]
        }

        with mock.patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_azure_provider(),
        ), mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk import (
                sqlserver_tde_encrypted_with_cmk,
            )

            check = sqlserver_tde_encrypted_with_cmk()
            result = check.execute()
            assert len(result) == 0

    def test_sql_servers_encryption_protector_service_managed(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        database = Database(
            id="id",
            name="name",
            type="type",
            location="location",
            managed_by="managed_by",
            tde_encryption=None,
        )
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION_ID: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    location="location",
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=[database],
                    encryption_protector=EncryptionProtector(
                        server_key_type="ServiceManaged"
                    ),
                )
            ]
        }

        with mock.patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_azure_provider(),
        ), mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk import (
                sqlserver_tde_encrypted_with_cmk,
            )

            check = sqlserver_tde_encrypted_with_cmk()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"SQL Server {sql_server_name} from subscription {AZURE_SUBSCRIPTION_ID} has TDE disabled without CMK."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION_ID
            assert result[0].resource_name == sql_server_name
            assert result[0].resource_id == sql_server_id
            assert result[0].location == "location"

    def test_sql_servers_database_encryption_disabled(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        database = Database(
            id="id",
            name="name",
            type="type",
            location="location",
            managed_by="managed_by",
            tde_encryption=TransparentDataEncryption(status="Disabled"),
        )
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION_ID: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    location="location",
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=[database],
                    encryption_protector=EncryptionProtector(
                        server_key_type="AzureKeyVault"
                    ),
                )
            ]
        }

        with mock.patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_azure_provider(),
        ), mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk import (
                sqlserver_tde_encrypted_with_cmk,
            )

            check = sqlserver_tde_encrypted_with_cmk()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"SQL Server {sql_server_name} from subscription {AZURE_SUBSCRIPTION_ID} has TDE disabled with CMK."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION_ID
            assert result[0].resource_name == sql_server_name
            assert result[0].resource_id == sql_server_id
            assert result[0].location == "location"

    def test_sql_servers_database_encryption_enabled(self):
        sqlserver_client = mock.MagicMock
        sql_server_name = "SQL Server Name"
        sql_server_id = str(uuid4())
        database = Database(
            id="id",
            name="name",
            type="type",
            location="location",
            managed_by="managed_by",
            tde_encryption=TransparentDataEncryption(status="Enabled"),
        )
        sqlserver_client.sql_servers = {
            AZURE_SUBSCRIPTION_ID: [
                Server(
                    id=sql_server_id,
                    name=sql_server_name,
                    location="location",
                    public_network_access="",
                    minimal_tls_version="",
                    administrators=None,
                    auditing_policies=None,
                    firewall_rules=None,
                    databases=[database],
                    encryption_protector=EncryptionProtector(
                        server_key_type="AzureKeyVault"
                    ),
                )
            ]
        }

        with mock.patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_azure_provider(),
        ), mock.patch(
            "prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk.sqlserver_client",
            new=sqlserver_client,
        ):
            from prowler.providers.azure.services.sqlserver.sqlserver_tde_encrypted_with_cmk.sqlserver_tde_encrypted_with_cmk import (
                sqlserver_tde_encrypted_with_cmk,
            )

            check = sqlserver_tde_encrypted_with_cmk()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"SQL Server {sql_server_name} from subscription {AZURE_SUBSCRIPTION_ID} has TDE enabled with CMK."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION_ID
            assert result[0].resource_name == sql_server_name
            assert result[0].resource_id == sql_server_id
            assert result[0].location == "location"
