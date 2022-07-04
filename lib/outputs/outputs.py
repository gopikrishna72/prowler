from csv import DictWriter

from colorama import Fore, Style

from config.config import csv_file_suffix
from lib.outputs.models import Check_Output_CSV
from lib.utils.utils import file_exists, open_file


def report(check_findings, output_options, audit_info):
    check_findings.sort(key=lambda x: x.region)

    csv_fields = []
    # check output options
    file_descriptors = {}
    if output_options.output_modes:
        if "csv" in output_options.output_modes:
            csv_fields = generate_csv_fields(audit_info.organizations_metadata)

        file_descriptors = fill_file_descriptors(
            output_options.output_modes,
            audit_info.audited_account,
            output_options.output_directory,
            csv_fields,
        )

    for finding in check_findings:
        # printing the finding ...

        color = set_report_color(finding.status)
        if output_options.is_quiet and "FAIL" in finding.status:
            print(
                f"{color}{finding.status}{Style.RESET_ALL} {finding.region}: {finding.status_extended}"
            )
        elif not output_options.is_quiet:
            print(
                f"{color}{finding.status}{Style.RESET_ALL} {finding.region}: {finding.status_extended}"
            )
        if file_descriptors:

            # sending the finding to input options
            if "csv" in file_descriptors:
                finding_output = Check_Output_CSV(
                    audit_info.audited_account,
                    audit_info.profile,
                    finding,
                    audit_info.organizations_metadata,
                )
                csv_writer = DictWriter(
                    file_descriptors["csv"], fieldnames=csv_fields, delimiter=";"
                )
                csv_writer.writerow(finding_output.__dict__)

    if file_descriptors:
        # Close all file descriptors
        for file_descriptor in file_descriptors:
            file_descriptors.get(file_descriptor).close()


def fill_file_descriptors(output_modes, audited_account, output_directory, csv_fields):
    file_descriptors = {}
    for output_mode in output_modes:
        if output_mode == "csv":
            filename = (
                f"{output_directory}/prowler-output-{audited_account}-{csv_file_suffix}"
            )
            if file_exists(filename):
                file_descriptor = open_file(
                    filename,
                    "a",
                )
            else:
                file_descriptor = open_file(
                    filename,
                    "a",
                )
                csv_header = [x.upper() for x in csv_fields]
                csv_writer = DictWriter(
                    file_descriptor, fieldnames=csv_header, delimiter=";"
                )
                csv_writer.writeheader()

            file_descriptors.update({output_mode: file_descriptor})
    return file_descriptors


def set_report_color(status):
    color = ""
    if status == "PASS":
        color = Fore.GREEN
    elif status == "FAIL":
        color = Fore.RED
    elif status == "ERROR":
        color = Fore.BLACK
    elif status == "WARNING":
        color = Fore.YELLOW
    else:
        raise Exception("Invalid Report Status. Must be PASS, FAIL, ERROR or WARNING")
    return color


def generate_csv_fields(organizations_metadata):
    csv_fields = []
    organizations_fields = [
        "account_email",
        "account_arn",
        "account_org",
        "account_tags",
    ]
    for field in Check_Output_CSV.__dict__["__annotations__"].keys():
        if not (not organizations_metadata and field in organizations_fields):
            csv_fields.append(field)
    return csv_fields
