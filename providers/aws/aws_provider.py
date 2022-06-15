from dataclasses import dataclass

from arnparse import arnparse
from boto3 import session

from lib.logger import logger


@dataclass
class AWS_Credentials:
    aws_access_key_id: str
    aws_session_token: str
    aws_secret_access_key: str


@dataclass
class AWS_Session_Info:
    profile: str
    credentials: AWS_Credentials


@dataclass
class Input_Data:
    profile: str
    role_name: str
    account_to_assume: str
    session_duration: int
    external_id: str


@dataclass
class AWS_Assume_Role:
    role_name: str
    account_to_assume: str
    session_duration: int
    external_id: str
    sts_session: session


################## AWS PROVIDER
class AWS_Provider:
    def __init__(self, session_info):
        self.aws_session = self.set_session(session_info)

    def get_session(self):
        return self.aws_session

    def set_session(self, session_info):
        try:
            if session_info.credentials:
                return session.Session(
                    profile_name=session_info.profile,
                    aws_access_key_id=session_info.credentials.aws_access_key_id,
                    aws_secret_access_key=session_info.credentials.aws_secret_access_key,
                    aws_session_token=session_info.credentials.aws_session_token,
                )
            else:
                return session.Session(profile_name=session_info.profile)
        except Exception as error:
            logger.critical(f"{error.__class__.__name__} -- {error}")
            quit()


def validate_credentials(validate_session):

    try:
        validate_credentials_client = validate_session.client("sts")
        validate_credentials_client.get_caller_identity()
    except Exception as error:
        logger.critical(f"{error.__class__.__name__} -- {error}")
        quit()


def provider_set_session(session_input):
    global aws_session
    global original_session
    session_info = AWS_Session_Info(
        session_input.profile, AWS_Credentials(None, None, None)
    )
    role_info = AWS_Assume_Role(
        session_input.role_name,
        session_input.account_to_assume,
        session_input.session_duration,
        session_input.external_id,
        None,
    )

    original_session = AWS_Provider(session_info).get_session()
    validate_credentials(original_session)

    if session_input.role_name and session_input.account_to_assume:
        logger.info("Assuming role ...")
        role_info.sts_session = original_session
        assumed_role_response = assume_role(role_info)
        session_info.credentials.assumed_access_key_id = assumed_role_response[
            "Credentials"
        ]["AccessKeyId"]
        session_info.credentials.assumed_secret_access_key = assumed_role_response[
            "Credentials"
        ]["SecretAccessKey"]
        session_info.credentials.assumed_session_token = assumed_role_response[
            "Credentials"
        ]["SessionToken"]

    aws_session = AWS_Provider(session_info).get_session()


def assume_role(role_info):

    try:
        sts_client = role_info.sts_session.client("sts")
        caller_identity = sts_client.get_caller_identity()
        arn_caller_identity = arnparse(caller_identity["Arn"])
        role_arn = f"arn:{arn_caller_identity.partition}:iam::{role_info.account_to_assume}:role/{role_info.role_name}"
        if role_info.external_id:
            assumed_credentials = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName="ProwlerProSession",
                DurationSeconds=role_info.session_duration,
                ExternalId=role_info.external_id,
            )
        else:
            assumed_credentials = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName="ProwlerProSession",
                DurationSeconds=role_info.session_duration,
            )
    except Exception as error:
        logger.critical(f"{error.__class__.__name__} -- {error}")
        quit()

    return assumed_credentials
