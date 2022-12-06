from prowler.lib.check.models import Check, Check_Report
from prowler.providers.aws.services.ec2.ec2_client import ec2_client
from prowler.providers.aws.services.ec2.lib.security_groups import check_security_group


class ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_mysql_3306(Check):
    def execute(self):
        findings = []
        check_ports = [3306]
        for security_group in ec2_client.security_groups:
            report = Check_Report(self.metadata())
            report.region = security_group.region
            report.resource_id = security_group.id
            report.status = "PASS"
            report.status_extended = f"Security group {security_group.name} ({security_group.id}) has not MySQL port 3306 open to the Internet."
            # Loop through every security group's ingress rule and check it
            for ingress_rule in security_group.ingress_rules:
                if check_security_group(
                    ingress_rule, "tcp", check_ports, any_address=True
                ):
                    report.status = "FAIL"
                    report.status_extended = f"Security group {security_group.name} ({security_group.id}) has MySQL port 3306 open to the Internet."
                    report.resource_id = security_group.id
                    break
            findings.append(report)

        return findings
