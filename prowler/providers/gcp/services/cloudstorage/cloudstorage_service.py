from pydantic import BaseModel

from prowler.lib.logger import logger
from prowler.providers.gcp.gcp_provider import generate_client


################## CloudStorage
class CloudStorage:
    def __init__(self, audit_info):
        self.service = "storage"
        self.api_version = "v1"
        self.project_id = audit_info.project_id
        self.client = generate_client(self.service, self.api_version, audit_info)
        self.buckets = []
        self.__get_buckets__()

    def __get_buckets__(self):
        try:
            request = self.client.buckets().list(project=self.project_id)
            while request is not None:
                response = request.execute()

                for bucket in response.get("items", []):
                    self.buckets.append(
                        Bucket(
                            name=bucket["name"],
                            id=bucket["id"],
                            region=bucket["location"],
                            uniform_bucket_level_access=bucket["iamConfiguration"][
                                "uniformBucketLevelAccess"
                            ]["enabled"],
                        )
                    )

                request = self.client.buckets().list_next(
                    previous_request=request, previous_response=response
                )
        except Exception as error:
            logger.error(
                f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )


class Bucket(BaseModel):
    name: str
    id: str
    region: str
    uniform_bucket_level_access: bool
