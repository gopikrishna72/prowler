from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.ssm.ssm_service import SSM

ssm_client = SSM(current_audit_info)
