from re import search
from unittest import mock
from uuid import uuid4

from providers.aws.services.sagemaker.sagemaker_service import SagemakerTrainingJob

AWS_REGION = "eu-west-1"
AWS_ACCOUNT_NUMBER = "123456789012"

test_training_job = "test-training-job"
training_job_arn = f"arn:aws:sagemaker:{AWS_REGION}:{AWS_ACCOUNT_NUMBER}:training-job/{test_training_job}"
subnet_id = "subnet-" + str(uuid4())


class Test_sagemaker_training_jobs_vpc_settings_configured:
    def test_no_training_jobs(self):
        sagemaker_client = mock.MagicMock
        sagemaker_client.sagemaker_training_jobs = []
        with mock.patch(
            "providers.aws.services.sagemaker.sagemaker_service.SageMaker",
            sagemaker_client,
        ):
            from providers.aws.services.sagemaker.sagemaker_training_jobs_vpc_settings_configured.sagemaker_training_jobs_vpc_settings_configured import (
                sagemaker_training_jobs_vpc_settings_configured,
            )

            check = sagemaker_training_jobs_vpc_settings_configured()
            result = check.execute()
            assert len(result) == 0

    def test_instance_traffic_encryption_enabled(self):
        sagemaker_client = mock.MagicMock
        sagemaker_client.sagemaker_training_jobs = []
        sagemaker_client.sagemaker_training_jobs.append(
            SagemakerTrainingJob(
                name=test_training_job,
                arn=training_job_arn,
                region=AWS_REGION,
                vpc_config_subnets=[subnet_id],
            )
        )
        with mock.patch(
            "providers.aws.services.sagemaker.sagemaker_service.SageMaker",
            sagemaker_client,
        ):
            from providers.aws.services.sagemaker.sagemaker_training_jobs_vpc_settings_configured.sagemaker_training_jobs_vpc_settings_configured import (
                sagemaker_training_jobs_vpc_settings_configured,
            )

            check = sagemaker_training_jobs_vpc_settings_configured()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert search(
                "has VPC settings for the training job volume and output enabled",
                result[0].status_extended,
            )
            assert result[0].resource_id == test_training_job
            assert result[0].resource_arn == training_job_arn

    def test_instance_traffic_encryption_disabled(self):
        sagemaker_client = mock.MagicMock
        sagemaker_client.sagemaker_training_jobs = []
        sagemaker_client.sagemaker_training_jobs.append(
            SagemakerTrainingJob(
                name=test_training_job,
                arn=training_job_arn,
                region=AWS_REGION,
            )
        )
        with mock.patch(
            "providers.aws.services.sagemaker.sagemaker_service.SageMaker",
            sagemaker_client,
        ):
            from providers.aws.services.sagemaker.sagemaker_training_jobs_vpc_settings_configured.sagemaker_training_jobs_vpc_settings_configured import (
                sagemaker_training_jobs_vpc_settings_configured,
            )

            check = sagemaker_training_jobs_vpc_settings_configured()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert search(
                "has VPC settings for the training job volume and output disabled",
                result[0].status_extended,
            )
            assert result[0].resource_id == test_training_job
            assert result[0].resource_arn == training_job_arn
