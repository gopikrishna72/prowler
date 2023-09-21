from prowler.lib.check.models import Check, Check_Report_AWS
from prowler.providers.aws.services.apigateway.apigateway_client import (
    apigateway_client,
)


class apigateway_endpoint_public_without_authorizer(Check):
    def execute(self):
        findings = []
        for rest_api in apigateway_client.rest_apis:
            report = Check_Report_AWS(self.metadata())
            report.region = rest_api.region
            report.resource_id = rest_api.name
            report.resource_arn = rest_api.arn
            report.resource_tags = rest_api.tags
            if rest_api.public_endpoint and not rest_api.authorizer:
                report.status = "FAIL"
                report.status_extended = f"API Gateway {rest_api.name} ID {rest_api.id} is internet accesible without an authorizer."
            else:
                report.status = "PASS"
                report.status_extended = (
                    f"API Gateway {rest_api.name} ID {rest_api.id} is {'internet accesible with an authorizer' if rest_api.public_endpoint else 'private'}."
                )
            findings.append(report)

        return findings
