from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.apigateway.apigateway_service import APIGateway

apigateway_client = APIGateway(current_audit_info)
