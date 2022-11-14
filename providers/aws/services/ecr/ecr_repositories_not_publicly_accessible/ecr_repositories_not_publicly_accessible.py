from lib.check.models import Check, Check_Report
from providers.aws.services.ecr.ecr_client import ecr_client


class ecr_repositories_not_publicly_accessible(Check):
    def execute(self):
        findings = []
        for repository in ecr_client.repositories:
            report = Check_Report(self.metadata)
            report.region = repository.region
            report.resource_id = repository.name
            report.resource_arn = repository.arn
            report.status = "PASS"
            report.status_extended = f"Repository {repository.name} is not open"
            if repository.policy:
                for statement in repository.policy["Statement"]:
                    if (
                        statement["Effect"] == "Allow"
                        and "AWS" in statement["Principal"]
                        and statement["Principal"]["AWS"] == "*"
                    ):
                        report.status = "FAIL"
                        report.status_extended = f"Repository {repository.name} policy may allow anonymous users to perform actions (Principal: '*')"
                        break

            findings.append(report)

        return findings
