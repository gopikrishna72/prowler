from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.securityhub.securityhub_service import SECURITYHUB

securityhub_client = SECURITYHUB(current_audit_info)
