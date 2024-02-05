from unittest.mock import patch

from azure.mgmt.sql.models import EncryptionProtector, TransparentDataEncryption

from prowler.providers.azure.services.sqlserver.sqlserver_service import (
    DatabaseServer,
    SQL_Server,
    SQLServer,
)
from tests.providers.azure.azure_fixtures import (
    AZURE_SUSCRIPTION,
    set_mocked_azure_audit_info,
)


def mock_sqlserver_get_sql_servers(_):
    database = DatabaseServer(
        id="id",
        name="name",
        type="type",
        location="location",
        managed_by="managed_by",
        tde_encryption=TransparentDataEncryption(status="Disabled"),
    )
    return {
        AZURE_SUSCRIPTION: [
            SQL_Server(
                id="id",
                name="name",
                public_network_access="public_network_access",
                minimal_tls_version="minimal_tls_version",
                administrators=None,
                auditing_policies=None,
                firewall_rules=None,
                encryption_protector=EncryptionProtector(
                    server_key_type="AzureKeyVault"
                ),
                databases=[database],
            )
        ]
    }


@patch(
    "prowler.providers.azure.services.sqlserver.sqlserver_service.SQLServer.__get_sql_servers__",
    new=mock_sqlserver_get_sql_servers,
)
class Test_SqlServer_Service:
    def test__get_client__(self):
        sql_server = SQLServer(set_mocked_azure_audit_info())
        assert (
            sql_server.clients[AZURE_SUSCRIPTION].__class__.__name__
            == "SqlManagementClient"
        )

    def test__get_sql_servers__(self):
        database = DatabaseServer(
            id="id",
            name="name",
            type="type",
            location="location",
            managed_by="managed_by",
            tde_encryption=TransparentDataEncryption(status="Disabled"),
        )
        sql_server = SQLServer(set_mocked_azure_audit_info())
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0].__class__.__name__
            == "SQL_Server"
        )
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].id == "id"
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].name == "name"
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0].public_network_access
            == "public_network_access"
        )
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0].minimal_tls_version
            == "minimal_tls_version"
        )
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].administrators is None
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].auditing_policies is None
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].firewall_rules is None
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][
                0
            ].encryption_protector.__class__.__name__
            == "EncryptionProtector"
        )
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].databases == [database]

    def test__get_databases__(self):
        sql_server = SQLServer(set_mocked_azure_audit_info())
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0].databases[0].__class__.__name__
            == "DatabaseServer"
        )
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].databases[0].id == "id"
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].databases[0].name == "name"
        assert sql_server.sql_servers[AZURE_SUSCRIPTION][0].databases[0].type == "type"
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0].databases[0].location
            == "location"
        )
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0].databases[0].managed_by
            == "managed_by"
        )
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0]
            .databases[0]
            .tde_encryption.__class__.__name__
            == "TransparentDataEncryption"
        )

    def test__get_transparent_data_encryption__(self):
        sql_server = SQLServer(set_mocked_azure_audit_info())
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0]
            .databases[0]
            .tde_encryption.__class__.__name__
            == "TransparentDataEncryption"
        )
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][0]
            .databases[0]
            .tde_encryption.status
            == "Disabled"
        )

    def test__get_encryption_protectors__(self):
        sql_server = SQLServer(set_mocked_azure_audit_info())
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][
                0
            ].encryption_protector.__class__.__name__
            == "EncryptionProtector"
        )
        assert (
            sql_server.sql_servers[AZURE_SUSCRIPTION][
                0
            ].encryption_protector.server_key_type
            == "AzureKeyVault"
        )

    def test__get_resource_group__(self):
        id = "/subscriptions/subscription_id/resourceGroups/resource_group/providers/Microsoft.Sql/servers/sql_server"
        sql_server = SQLServer(set_mocked_azure_audit_info())
        assert sql_server.__get_resource_group__(id) == "resource_group"
