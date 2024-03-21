from unittest import mock
from uuid import uuid4

from tests.providers.azure.azure_fixtures import DOMAIN


class Test_entra_ensure_security_default_enabled:
    def test_entra_no_tenants(self):
        entra_client = mock.MagicMock

        with mock.patch(
            "prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled.entra_client",
            new=entra_client,
        ):
            from prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled import (
                entra_ensure_security_default_enabled,
            )

            entra_client.security_default = {}

            check = entra_ensure_security_default_enabled()
            result = check.execute()
            assert len(result) == 0

    def test_entra_tenant_empty(self):
        entra_client = mock.MagicMock

        with mock.patch(
            "prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled.entra_client",
            new=entra_client,
        ):
            from prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled import (
                entra_ensure_security_default_enabled,
            )

            entra_client.security_default = {DOMAIN: {}}

            check = entra_ensure_security_default_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert result[0].status_extended == "Entra security defaults is diabled."
            assert result[0].subscription == f"Tenant: '{DOMAIN}'"
            assert result[0].resource_name == "Security Default"
            assert result[0].resource_id == "Security Default"

    def test_entra_security_default_enabled(self):
        entra_client = mock.MagicMock

        with mock.patch(
            "prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled.entra_client",
            new=entra_client,
        ):
            from prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled import (
                entra_ensure_security_default_enabled,
            )
            from prowler.providers.azure.services.entra.entra_service import (
                SecurityDefault,
            )

            id = str(uuid4())

            entra_client.security_default = {
                DOMAIN: SecurityDefault(id=id, name="Sec Default", is_enabled=True)
            }

            check = entra_ensure_security_default_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert result[0].status_extended == "Entra security defaults is enabled."
            assert result[0].subscription == f"Tenant: '{DOMAIN}'"
            assert result[0].resource_name == "Sec Default"
            assert result[0].resource_id == id

    def test_entra_security_default_disabled(self):
        entra_client = mock.MagicMock

        with mock.patch(
            "prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled.entra_client",
            new=entra_client,
        ):
            from prowler.providers.azure.services.entra.entra_ensure_security_default_enabled.entra_ensure_security_default_enabled import (
                entra_ensure_security_default_enabled,
            )
            from prowler.providers.azure.services.entra.entra_service import (
                SecurityDefault,
            )

            id = str(uuid4())

            entra_client.security_default = {
                DOMAIN: SecurityDefault(id=id, name="Sec Default", is_enabled=False)
            }

            check = entra_ensure_security_default_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert result[0].status_extended == "Entra security defaults is diabled."
            assert result[0].subscription == f"Tenant: '{DOMAIN}'"
            assert result[0].resource_name == "Sec Default"
            assert result[0].resource_id == id
