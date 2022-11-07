import datetime
import threading
from dataclasses import dataclass

from lib.logger import logger
from providers.aws.aws_provider import generate_regional_clients


################### CLOUDTRAIL
class Cloudtrail:
    def __init__(self, audit_info):
        self.service = "cloudtrail"
        self.session = audit_info.audit_session
        self.audited_account = audit_info.audited_account
        self.regional_clients = generate_regional_clients(self.service, audit_info)
        self.trails = []
        self.__threading_call__(self.__get_trails__)
        self.__get_trail_status__()

    def __get_session__(self):
        return self.session

    def __threading_call__(self, call):
        threads = []
        for regional_client in self.regional_clients.values():
            threads.append(threading.Thread(target=call, args=(regional_client,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def __get_trails__(self, regional_client):
        logger.info("Cloudtrail - Getting trails...")
        try:
            describe_trails = regional_client.describe_trails()["trailList"]
            if describe_trails:
                for trail in describe_trails:
                    if "KmsKeyId" in trail:
                        kms_key_id = trail["KmsKeyId"]
                    else:
                        kms_key_id = None
                    self.trails.append(
                        Trail(
                            name=trail["Name"],
                            is_multiregion=trail["IsMultiRegionTrail"],
                            home_region=trail["HomeRegion"],
                            trail_arn=trail["TrailARN"],
                            region=regional_client.region,
                            is_logging=False,
                            log_file_validation_enabled=trail[
                                "LogFileValidationEnabled"
                            ],
                            latest_cloudwatch_delivery_time=None,
                            s3_bucket=trail["S3BucketName"],
                            kms_key=kms_key_id,
                        )
                    )
            else:
                self.trails.append(
                    Trail(
                        name=None,
                        is_multiregion=None,
                        home_region=None,
                        trail_arn=None,
                        region=regional_client.region,
                        is_logging=None,
                        log_file_validation_enabled=None,
                        latest_cloudwatch_delivery_time=None,
                        s3_bucket=None,
                        kms_key=None,
                    )
                )

        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}: {error}"
            )

    def __get_trail_status__(self):
        logger.info("Cloudtrail - Getting trail status")
        try:
            for trail in self.trails:
                for region, client in self.regional_clients.items():
                    if trail.region == region and trail.name:
                        status = client.get_trail_status(Name=trail.trail_arn)
                        trail.is_logging = status["IsLogging"]
                        if "LatestCloudWatchLogsDeliveryTime" in status:
                            trail.latest_cloudwatch_delivery_time = status[
                                "LatestCloudWatchLogsDeliveryTime"
                            ]

        except Exception as error:
            logger.error(f"{client.region} -- {error.__class__.__name__}: {error}")


@dataclass
class Trail:
    name: str
    is_multiregion: bool
    home_region: str
    trail_arn: str
    region: str
    is_logging: bool
    log_file_validation_enabled: bool
    latest_cloudwatch_delivery_time: datetime
    s3_bucket: str
    kms_key: str

    def __init__(
        self,
        name,
        is_multiregion,
        home_region,
        trail_arn,
        region,
        is_logging,
        log_file_validation_enabled,
        latest_cloudwatch_delivery_time,
        s3_bucket,
        kms_key,
    ):
        self.name = name
        self.is_multiregion = is_multiregion
        self.home_region = home_region
        self.trail_arn = trail_arn
        self.region = region
        self.is_logging = is_logging
        self.log_file_validation_enabled = log_file_validation_enabled
        self.latest_cloudwatch_delivery_time = latest_cloudwatch_delivery_time
        self.s3_bucket = s3_bucket
        self.kms_key = kms_key
