from arnparse import arnparse
from boto3 import session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

from lib.arn.arn import arn_parsing
from lib.logger import logger
from providers.aws.models import AWS_Assume_Role, AWS_Audit_Info, AWS_Credentials


################## AWS PROVIDER
class AWS_Provider:
    def __init__(self, audit_info):
        logger.info("Instantiating aws provider ...")
        self.aws_session = self.set_session(audit_info)
        self.role_info = audit_info.assumed_role_info

    def get_session(self):
        return self.aws_session

    def set_session(self, audit_info):
        try:
            if audit_info.credentials:
                # If we receive a credentials object filled is coming form an assumed role, so renewal is needed
                logger.info("Creating session for assumed role ...")
                # From botocore we can use RefreshableCredentials class, which has an attribute (refresh_using)
                # that needs to be a method without arguments that retrieves a new set of fresh credentials
                # asuming the role again. -> https://github.com/boto/botocore/blob/098cc255f81a25b852e1ecdeb7adebd94c7b1b73/botocore/credentials.py#L395
                assumed_refreshable_credentials = RefreshableCredentials(
                    access_key=audit_info.credentials.aws_access_key_id,
                    secret_key=audit_info.credentials.aws_secret_access_key,
                    token=audit_info.credentials.aws_session_token,
                    expiry_time=audit_info.credentials.expiration,
                    refresh_using=self.refresh,
                    method="sts-assume-role",
                )
                # Here we need the botocore session since it needs to use refreshable credentials
                assumed_botocore_session = get_session()
                assumed_botocore_session._credentials = assumed_refreshable_credentials
                assumed_botocore_session.set_config_variable("region", "us-east-1")

                return session.Session(
                    profile_name=audit_info.profile,
                    botocore_session=assumed_botocore_session,
                )
            # If we do not receive credentials start the session using the profile
            else:
                logger.info("Creating session for not assumed identity ...")
                return session.Session(profile_name=audit_info.profile)
        except Exception as error:
            logger.critical(f"{error.__class__.__name__} -- {error}")
            quit()

    # Refresh credentials method using assume role
    # This method is called "adding ()" to the name, so it cannot accept arguments
    # https://github.com/boto/botocore/blob/098cc255f81a25b852e1ecdeb7adebd94c7b1b73/botocore/credentials.py#L570
    def refresh(self):
        logger.info("Refreshing assumed credentials...")

        response = assume_role(self.role_info)
        refreshed_credentials = dict(
            # Keys of the dict has to be the same as those that are being searched in the parent class
            # https://github.com/boto/botocore/blob/098cc255f81a25b852e1ecdeb7adebd94c7b1b73/botocore/credentials.py#L609
            access_key=response["Credentials"]["AccessKeyId"],
            secret_key=response["Credentials"]["SecretAccessKey"],
            token=response["Credentials"]["SessionToken"],
            expiry_time=response["Credentials"]["Expiration"].isoformat(),
        )
        logger.info("Refreshed Credentials:")
        logger.info(refreshed_credentials)
        return refreshed_credentials


def provider_set_session(
    input_profile, input_role, input_session_duration, input_external_id, input_regions
):

    # Mark variable that stores all the info about the audit as global
    global current_audit_info

    assumed_session = None

    # Setting session
    current_audit_info = AWS_Audit_Info(
        original_session=None,
        audit_session=None,
        audited_account=None,
        audited_partition=None,
        profile=input_profile,
        credentials=None,
        assumed_role_info=AWS_Assume_Role(
            role_arn=input_role,
            session_duration=input_session_duration,
            external_id=input_external_id,
        ),
        audited_regions=input_regions,
    )

    logger.info("Generating original session ...")
    # Create an global original session using only profile/basic credentials info
    current_audit_info.original_session = AWS_Provider(current_audit_info).get_session()
    logger.info("Validating credentials ...")
    # Verificate if we have valid credentials
    caller_identity = validate_credentials(current_audit_info.original_session)

    logger.info("Credentials validated")
    logger.info(f"Original caller identity UserId : {caller_identity['UserId']}")
    logger.info(f"Original caller identity ARN : {caller_identity['Arn']}")

    current_audit_info.audited_account = caller_identity["Account"]
    current_audit_info.audited_partition = arnparse(caller_identity["Arn"]).partition

    logger.info("Checking if role assumption is needed ...")
    if current_audit_info.assumed_role_info.role_arn:
        # Check if role arn is valid
        try:
            # this returns the arn already parsed, calls arnparse, into a dict to be used when it is needed to access its fields
            role_arn_parsed = arn_parsing(current_audit_info.assumed_role_info.role_arn)

        except Exception as error:
            logger.critical(f"{error.__class__.__name__} -- {error}")
            quit()

        else:
            logger.info(
                f"Assuming role {current_audit_info.assumed_role_info.role_arn}"
            )
            # Assume the role
            assumed_role_response = assume_role()
            logger.info("Role assumed")
            # Set the info needed to create a session with an assumed role
            current_audit_info.credentials = AWS_Credentials(
                aws_access_key_id=assumed_role_response["Credentials"]["AccessKeyId"],
                aws_session_token=assumed_role_response["Credentials"]["SessionToken"],
                aws_secret_access_key=assumed_role_response["Credentials"][
                    "SecretAccessKey"
                ],
                expiration=assumed_role_response["Credentials"]["Expiration"],
            )
            assumed_session = AWS_Provider(current_audit_info).get_session()

    if assumed_session:
        logger.info("Audit session is the new session created assuming role")
        current_audit_info.audit_session = assumed_session
        current_audit_info.audited_account = role_arn_parsed.account_id
        current_audit_info.audited_partition = role_arn_parsed.partition
    else:
        logger.info("Audit session is the original one")
        current_audit_info.audit_session = current_audit_info.original_session


def validate_credentials(validate_session):
    try:
        validate_credentials_client = validate_session.client("sts")
        caller_identity = validate_credentials_client.get_caller_identity()
    except Exception as error:
        logger.critical(f"{error.__class__.__name__} -- {error}")
        quit()
    else:
        return caller_identity


def assume_role():

    try:
        # set the info to assume the role from the partition, account and role name
        sts_client = current_audit_info.original_session.client("sts")
        # If external id, set it to the assume role api call
        if current_audit_info.assumed_role_info.external_id:
            assumed_credentials = sts_client.assume_role(
                RoleArn=current_audit_info.assumed_role_info.role_arn,
                RoleSessionName="ProwlerProAsessmentSession",
                DurationSeconds=current_audit_info.assumed_role_info.session_duration,
                ExternalId=current_audit_info.assumed_role_info.external_id,
            )
        # else assume the role without the external id
        else:
            assumed_credentials = sts_client.assume_role(
                RoleArn=current_audit_info.assumed_role_info.role_arn,
                RoleSessionName="ProwlerProAsessmentSession",
                DurationSeconds=current_audit_info.assumed_role_info.session_duration,
            )
    except Exception as error:
        logger.critical(f"{error.__class__.__name__} -- {error}")
        quit()

    else:
        return assumed_credentials
