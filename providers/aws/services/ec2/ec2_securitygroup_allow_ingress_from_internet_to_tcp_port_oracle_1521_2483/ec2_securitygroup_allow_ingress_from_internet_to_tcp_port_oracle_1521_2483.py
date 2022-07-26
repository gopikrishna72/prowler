from lib.check.models import Check, Check_Report
from providers.aws.services.ec2.ec2_service import ec2_client


class ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_oracle_1521_2483(Check):
    def execute(self):
        findings = []
        check_port_1 = 1521
        check_port_2 = 2483
        for security_group in ec2_client.security_groups:
            public = False
            report = Check_Report(self.metadata)
            report.region = security_group.region
            for ingress_rule in security_group.ingress_rules:
                if "0.0.0.0/0" in str(ingress_rule["IpRanges"]) or "::/0" in str(
                    ingress_rule["Ipv6Ranges"]
                ):
                    if ingress_rule["IpProtocol"] == "-1":
                        public = True
                    elif (
                        ingress_rule["FromPort"] == check_port_1
                        and ingress_rule["ToPort"] == check_port_1
                        or ingress_rule["FromPort"] == check_port_2
                        and ingress_rule["ToPort"] == check_port_2
                    ):
                        public = True
            if not public:
                report.status = "PASS"
                report.status_extended = f"Security group {security_group.name} ({security_group.id}) has not Oracle ports open to the Internet."
                report.resource_id = security_group.id
            else:
                report.status = "FAIL"
                report.status_extended = f"Security group {security_group.name} ({security_group.id}) has Oracle ports open to the Internet."
                report.resource_id = security_group.id
            findings.append(report)

        return findings
