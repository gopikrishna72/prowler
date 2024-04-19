from unittest.mock import patch

from prowler.providers.gcp.services.gke.gke_service import GKE
from tests.providers.gcp.gcp_fixtures import (
    GCP_PROJECT_ID,
    mock_api_client,
    mock_is_api_active,
    set_mocked_gcp_provider,
)


@patch(
    "prowler.providers.gcp.lib.service.service.GCPService.__is_api_active__",
    new=mock_is_api_active,
)
@patch(
    "prowler.providers.gcp.lib.service.service.GCPService.__generate_client__",
    new=mock_api_client,
)
class Test_GKE_Service:
    def test__get_service__(self):
        api_keys_client = GKE(set_mocked_gcp_provider())
        assert api_keys_client.service == "container"

    def test__get_project_ids__(self):
        api_keys_client = GKE(set_mocked_gcp_provider())
        assert api_keys_client.project_ids.__class__.__name__ == "list"

    def test__get_locations__(self):
        api_keys_client = GKE(set_mocked_gcp_provider(project_ids=[GCP_PROJECT_ID]))
        assert len(api_keys_client.locations) == 1

        assert api_keys_client.locations[0].name == "eu-west1"
        assert api_keys_client.locations[0].project_id == GCP_PROJECT_ID

    def test__get_clusters__(self):
        api_keys_client = GKE(set_mocked_gcp_provider(project_ids=[GCP_PROJECT_ID]))

        assert len(api_keys_client.clusters) == 2

        assert api_keys_client.clusters["cluster1_id"].name == "cluster1"
        assert api_keys_client.clusters["cluster1_id"].id.__class__.__name__ == "str"
        assert api_keys_client.clusters["cluster1_id"].project_id == GCP_PROJECT_ID
        assert api_keys_client.clusters["cluster1_id"].location == "eu-west1"
        assert (
            api_keys_client.clusters["cluster1_id"].service_account
            == "service_account1"
        )
        assert len(api_keys_client.clusters["cluster1_id"].node_pools) == 1
        assert (
            api_keys_client.clusters["cluster1_id"].node_pools[0].name == "node_pool1"
        )
        assert api_keys_client.clusters["cluster1_id"].node_pools[0].locations == [
            "cluster1_location1"
        ]
        assert (
            api_keys_client.clusters["cluster1_id"].node_pools[0].service_account
            == "service_account1"
        )

        assert api_keys_client.clusters["cluster2_id"].name == "cluster2"
        assert api_keys_client.clusters["cluster2_id"].id.__class__.__name__ == "str"
        assert api_keys_client.clusters["cluster2_id"].project_id == GCP_PROJECT_ID
        assert api_keys_client.clusters["cluster2_id"].location == "eu-west1"
        assert (
            api_keys_client.clusters["cluster2_id"].service_account
            == "service_account2"
        )
        assert len(api_keys_client.clusters["cluster2_id"].node_pools) == 2
        assert (
            api_keys_client.clusters["cluster2_id"].node_pools[0].name == "node_pool2"
        )
        assert api_keys_client.clusters["cluster2_id"].node_pools[0].locations == [
            "cluster2_location1"
        ]
        assert (
            api_keys_client.clusters["cluster2_id"].node_pools[0].service_account
            == "service_account2"
        )
        assert (
            api_keys_client.clusters["cluster2_id"].node_pools[1].name == "node_pool3"
        )
        assert api_keys_client.clusters["cluster2_id"].node_pools[1].locations == [
            "cluster2_location2"
        ]
        assert (
            api_keys_client.clusters["cluster2_id"].node_pools[1].service_account
            == "service_account3"
        )
