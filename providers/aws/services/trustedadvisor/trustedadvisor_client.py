from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.trustedadvisor.trustedadvisor_service import TrustedAdvisor

trustedadvisor_client = TrustedAdvisor(current_audit_info)
