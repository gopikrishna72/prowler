from unittest import mock

import botocore
from boto3 import client
from mock import patch
from moto import mock_apigatewayv2

AWS_REGION = "us-east-1"

# Mocking ApiGatewayV2 Calls
make_api_call = botocore.client.BaseClient._make_api_call
# Rationale -> https://github.com/boto/botocore/blob/develop/botocore/client.py#L810:L816
#
# We have to mock every AWS API call using Boto3
def mock_make_api_call(self, operation_name, kwarg):
    if operation_name == "GetAuthorizers":
        return {"Items": [{"AuthorizerId": "authorizer-id", "Name": "test-authorizer"}]}
    elif operation_name == "GetStages":
        return {
            "Items": [
                {
                    "AccessLogSettings": {
                        "DestinationArn": "string",
                        "Format": "string",
                    },
                    "StageName": "test-stage",
                }
            ]
        }
    return make_api_call(self, operation_name, kwarg)


@patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call)
class Test_apigatewayv2_authorizers_enabled:
    @mock_apigatewayv2
    def test_apigateway_no_apis(self):
        from providers.aws.lib.audit_info.audit_info import current_audit_info
        from providers.aws.services.apigatewayv2.apigatewayv2_service import (
            ApiGatewayV2,
        )

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "providers.aws.services.apigatewayv2.apigatewayv2_authorizers_enabled.apigatewayv2_authorizers_enabled.apigatewayv2_client",
            new=ApiGatewayV2(current_audit_info),
        ):
            # Test Check
            from providers.aws.services.apigatewayv2.apigatewayv2_authorizers_enabled.apigatewayv2_authorizers_enabled import (
                apigatewayv2_authorizers_enabled,
            )

            check = apigatewayv2_authorizers_enabled()
            result = check.execute()

            assert len(result) == 0

    @mock_apigatewayv2
    def test_apigateway_one_api_with_authorizer(self):
        # Create ApiGatewayV2 Mocked Resources
        apigatewayv2_client = client("apigatewayv2", region_name=AWS_REGION)
        # Create ApiGatewayV2 API
        api = apigatewayv2_client.create_api(Name="test-api", ProtocolType="HTTP")
        apigatewayv2_client.create_authorizer(
            ApiId=api["ApiId"],
            AuthorizerType="REQUEST",
            IdentitySource=[],
            Name="auth1",
            AuthorizerPayloadFormatVersion="2.0",
        )
        from providers.aws.lib.audit_info.audit_info import current_audit_info
        from providers.aws.services.apigatewayv2.apigatewayv2_service import (
            ApiGatewayV2,
        )

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "providers.aws.services.apigatewayv2.apigatewayv2_authorizers_enabled.apigatewayv2_authorizers_enabled.apigatewayv2_client",
            new=ApiGatewayV2(current_audit_info),
        ):
            # Test Check
            from providers.aws.services.apigatewayv2.apigatewayv2_authorizers_enabled.apigatewayv2_authorizers_enabled import (
                apigatewayv2_authorizers_enabled,
            )

            check = apigatewayv2_authorizers_enabled()
            result = check.execute()

            assert result[0].status == "PASS"
            assert len(result) == 1
            assert (
                result[0].status_extended
                == f"API Gateway V2 test-api ID {api['ApiId']} has authorizer configured."
            )
            assert result[0].resource_id == "test-api"

    @mock_apigatewayv2
    def test_bad_response(self):
        mock_client = mock.MagicMock()

        with mock.patch(
            "providers.aws.services.apigatewayv2.apigatewayv2_authorizers_enabled.apigatewayv2_authorizers_enabled.apigatewayv2_client",
            new=mock_client,
        ):
            # Test Check
            from providers.aws.services.apigatewayv2.apigatewayv2_authorizers_enabled.apigatewayv2_authorizers_enabled import (
                apigatewayv2_authorizers_enabled,
            )

            check = apigatewayv2_authorizers_enabled()
            result = check.execute()

            assert len(result) == 0
