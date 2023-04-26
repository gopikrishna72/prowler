from prowler.lib.check.models import Check, Check_Report_AWS
from prowler.providers.aws.services.vpc.vpc_client import vpc_client
from prowler.providers.aws.services.workspaces.workspaces_client import (
    workspaces_client,
)


class workspaces_vpc_2private_1public_subnets_nat(Check):
    def execute(self):
        findings = []
        for workspace in workspaces_client.workspaces:
            report = Check_Report_AWS(self.metadata())
            report.region = workspace.region
            report.resource_id = workspace.id
            report.resource_arn = workspace.arn
            report.resource_tags = workspace.tags
            report.status = "PASS"
            report.status_extended = f"Worspace {workspace.id} it's in a VPC wich has 1 public with nat gateway and 2 private subnets"
            # Find the vpc id for the subnet in the vpc_client
            vpc_id = False
            for subnet in vpc_client.vpc_subnets:
                if subnet.id == workspace.subnet_id:
                    vpc_id = subnet.vpc_id
                    break
            # Get the vpc object from the vpc_client
            vpc_object = False
            for vpc in vpc_client.vpcs:
                if vpc.id == vpc_id:
                    vpc_object = vpc
                    break
            # Analyze VPC subnets
            public_subnets = 0
            private_subnets = 0
            public_subnet_nat_gateway = False
            if vpc_object:
                for vpc_subnet in vpc_object.subnets:
                    if vpc_subnet.public:
                        public_subnets += 1
                        if vpc_subnet.nat_gateway:
                            public_subnet_nat_gateway = True
                        # Check NAT Gateway here
                    if not vpc_subnet.public:
                        private_subnets += 1
            if (
                public_subnets < 1
                or private_subnets < 2
                or not public_subnet_nat_gateway
            ):
                report.status = "FAIL"
                report.status_extended = "Worspaces VPC has not 1 public with nat gateaway and 2 private subnets"

            findings.append(report)
        return findings
