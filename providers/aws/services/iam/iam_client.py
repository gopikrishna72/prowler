from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.iam.iam_service import IAM

iam_client = IAM(current_audit_info)
