from prowler.lib.logger import logger
from prowler.providers.aws.services.ec2.ec2_client import ec2_client


def fixer(region):
    """
    Enable IMDSv2 in a region.
    Requires the ec2:ModifyInstanceMetadataOptions permission:
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "ec2:ModifyInstanceMetadataOptions",
                "Resource": "*"
            }
        ]
    }
    Args:
        region (str): AWS region
    Returns:
        bool: True if IMDSv2 is enabled, False otherwise
    """

    try:
        regional_client = ec2_client.regional_clients[region]
        return (
            regional_client.modify_instance_metadata_options(HttpTokens="required")[
                "HttpTokens"
            ]
            == "required"
        )
    except Exception as error:
        logger.error(
            f"{region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
        )
        return False
