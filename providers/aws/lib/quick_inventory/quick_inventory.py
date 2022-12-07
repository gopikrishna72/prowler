from alive_progress import alive_bar
from colorama import Fore, Style
from tabulate import tabulate

from config.config import orange_color, output_file_timestamp
from lib.logger import logger
from providers.aws.lib.audit_info.models import AWS_Audit_Info


def quick_inventory(audit_info: AWS_Audit_Info, output_directory: str):
    print(
        f"-=- Running Quick Inventory for AWS Account {Fore.YELLOW}{audit_info.audited_account}{Style.RESET_ALL} -=-\n"
    )
    resources = []
    output_file = f"{output_directory}/prowler-inventory-{audit_info.audited_account}-{output_file_timestamp}.csv"
    # If not inputed regions, check all of them
    if not audit_info.audited_regions:
        # EC2 client for describing all regions
        ec2_client = audit_info.audit_session.client("ec2")
        # Get all the available regions
        audit_info.audited_regions = [
            region["RegionName"] for region in ec2_client.describe_regions()["Regions"]
        ]

    with alive_bar(
        total=len(audit_info.audited_regions),
        ctrl_c=False,
        bar="blocks",
        spinner="classic",
        stats=False,
        enrich_print=False,
    ) as bar:
        for region in sorted(audit_info.audited_regions):
            bar.title = f"-> Scanning {orange_color}{region}{Style.RESET_ALL} region"
            resources_in_region = []
            try:
                # If us-east-1 get IAM resources
                iam_client = audit_info.audit_session.client("iam")
                if region == "us-east-1":

                    get_roles_paginator = iam_client.get_paginator("list_roles")
                    for page in get_roles_paginator.paginate():
                        for role in page["Roles"]:
                            resources_in_region.append(role["Arn"])

                    get_users_paginator = iam_client.get_paginator("list_users")
                    for page in get_users_paginator.paginate():
                        for user in page["Users"]:
                            resources_in_region.append(user["Arn"])

                    get_groups_paginator = iam_client.get_paginator("list_groups")
                    for page in get_groups_paginator.paginate():
                        for group in page["Groups"]:
                            resources_in_region.append(group["Arn"])

                    get_policies_paginator = iam_client.get_paginator("list_policies")
                    for page in get_policies_paginator.paginate(Scope="Local"):
                        for policy in page["Policies"]:
                            resources_in_region.append(policy["Arn"])

                    for saml_provider in iam_client.list_saml_providers()[
                        "SAMLProviderList"
                    ]:
                        resources_in_region.append(saml_provider["Arn"])

                client = audit_info.audit_session.client(
                    "resourcegroupstaggingapi", region_name=region
                )
                # Get all the resources
                resources_count = 0
                get_resources_paginator = client.get_paginator("get_resources")
                for page in get_resources_paginator.paginate():
                    resources_count += len(page["ResourceTagMappingList"])
                    for resource in page["ResourceTagMappingList"]:
                        resources_in_region.append(resource["ResourceARN"])
                bar()
                print(
                    f"Found {Fore.GREEN}{len(resources_in_region)}{Style.RESET_ALL} resources in region {Fore.YELLOW}{region}{Style.RESET_ALL}"
                )
                print("\n")

            except Exception as error:
                logger.error(
                    f"{region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
                )
                bar()

            resources.extend(resources_in_region)
        bar.title = f"-> {Fore.GREEN}Quick Inventory completed!{Style.RESET_ALL}"

    inventory_table = create_inventory_table(resources)

    print(
        f"\nQuick Inventory of AWS Account {Fore.YELLOW}{audit_info.audited_account}{Style.RESET_ALL}:"
    )

    print(tabulate(inventory_table, headers="keys", tablefmt="rounded_grid"))

    print(f"\nTotal resources found: {Fore.GREEN}{len(resources)}{Style.RESET_ALL}")

    print(f"\nMore details in file: {Fore.GREEN}{output_file}{Style.RESET_ALL}")


def create_inventory_table(resources: list):

    services = {}
    # { "S3":
    #       123,
    #   "IAM":
    #       239,
    # }
    resources_type = {}
    # { "S3":
    #       "Buckets": 13,
    #   "IAM":
    #       "Roles": 143,
    #       "Users": 22,
    # }
    for resource in sorted(resources):
        service = resource.split(":")[2]
        if service not in services:
            services[service] = 0
        services[service] += 1

        if service == "s3":
            resource_type = "bucket"
        else:
            resource_type = resource.split(":")[5].split("/")[0]
        if service not in resources_type:
            resources_type[service] = {}
        if resource_type not in resources_type[service]:
            resources_type[service][resource_type] = 0
        resources_type[service][resource_type] += 1

    # Add results to inventory table
    inventory_table = {
        "Service": [],
        "Total": [],
        "Count per resource types": [],
    }
    for service in services:
        summary = ""
        inventory_table["Service"].append(service)
        inventory_table["Total"].append(services[service])
        for resource_type in resources_type[service]:
            summary += f"{resource_type} {resources_type[service][resource_type]}\n"
        inventory_table["Count per resource types"].append(summary)

    return inventory_table
