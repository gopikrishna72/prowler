import sys

from colorama import Fore, Style
from tabulate import tabulate

from prowler.config.config import orange_color
from prowler.lib.check.models import Check_Report
from prowler.lib.logger import logger
from prowler.lib.outputs.compliance.aws_well_architected_framework import (
    write_compliance_row_aws_well_architected_framework,
)
from prowler.lib.outputs.compliance.cis import write_compliance_row_cis
from prowler.lib.outputs.compliance.ens_rd2022_aws import (
    write_compliance_row_ens_rd2022_aws,
)
from prowler.lib.outputs.compliance.generic import write_compliance_row_generic
from prowler.lib.outputs.compliance.iso27001_2013_aws import (
    write_compliance_row_iso27001_2013_aws,
)
from prowler.lib.outputs.compliance.mitre_attack_aws import (
    write_compliance_row_mitre_attack_aws,
)


def add_manual_controls(
    output_options, provider, file_descriptors, input_compliance_frameworks
):
    try:
        # Check if MANUAL control was already added to output
        if "manual_check" in output_options.bulk_checks_metadata:
            manual_finding = Check_Report(
                output_options.bulk_checks_metadata["manual_check"].json()
            )
            manual_finding.status = "MANUAL"
            manual_finding.status_extended = "Manual check"
            manual_finding.resource_id = "manual_check"
            manual_finding.resource_name = "Manual check"
            manual_finding.region = ""
            manual_finding.location = ""
            manual_finding.project_id = ""
            manual_finding.subscription = ""
            manual_finding.namespace = ""
            fill_compliance(
                output_options,
                manual_finding,
                provider,
                file_descriptors,
                input_compliance_frameworks,
            )
            del output_options.bulk_checks_metadata["manual_check"]
    except Exception as error:
        logger.error(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
        )


def get_check_compliance_frameworks_in_input(
    check_id, bulk_checks_metadata, input_compliance_frameworks
):
    """get_check_compliance_frameworks_in_input returns a list of Compliance for the given check if the compliance framework is present in the input compliance to execute"""
    check_compliances = []
    if bulk_checks_metadata and bulk_checks_metadata[check_id]:
        for compliance in bulk_checks_metadata[check_id].Compliance:
            compliance_name = ""
            if compliance.Version:
                compliance_name = (
                    compliance.Framework.lower()
                    + "_"
                    + compliance.Version.lower()
                    + "_"
                    + compliance.Provider.lower()
                )
            else:
                compliance_name = (
                    compliance.Framework.lower() + "_" + compliance.Provider.lower()
                )
            if compliance_name.replace("-", "_") in input_compliance_frameworks:
                check_compliances.append(compliance)

    return check_compliances


def fill_compliance(
    output_options, finding, provider, file_descriptors, input_compliance_frameworks
):
    try:
        # We have to retrieve all the check's compliance requirements and get the ones matching with the input ones
        check_compliances = get_check_compliance_frameworks_in_input(
            finding.check_metadata.CheckID,
            output_options.bulk_checks_metadata,
            input_compliance_frameworks,
        )

        for compliance in check_compliances:
            if compliance.Framework == "ENS" and compliance.Version == "RD2022":
                write_compliance_row_ens_rd2022_aws(
                    file_descriptors, finding, compliance, output_options, provider
                )

            elif compliance.Framework == "CIS":
                write_compliance_row_cis(
                    file_descriptors,
                    finding,
                    compliance,
                    output_options,
                    provider,
                    input_compliance_frameworks,
                )

            elif (
                "AWS-Well-Architected-Framework" in compliance.Framework
                and compliance.Provider == "AWS"
            ):
                write_compliance_row_aws_well_architected_framework(
                    file_descriptors, finding, compliance, output_options, provider
                )

            elif (
                compliance.Framework == "ISO27001"
                and compliance.Version == "2013"
                and compliance.Provider == "AWS"
            ):
                write_compliance_row_iso27001_2013_aws(
                    file_descriptors, finding, compliance, output_options, provider
                )

            elif (
                compliance.Framework == "MITRE-ATTACK"
                and compliance.Version == ""
                and compliance.Provider == "AWS"
            ):
                write_compliance_row_mitre_attack_aws(
                    file_descriptors, finding, compliance, output_options, provider
                )

            else:
                write_compliance_row_generic(
                    file_descriptors, finding, compliance, output_options, provider
                )

    except Exception as error:
        logger.error(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
        )


def display_compliance_table(
    findings: list,
    bulk_checks_metadata: dict,
    compliance_framework: str,
    output_filename: str,
    output_directory: str,
    compliance_overview: bool,
):
    try:
        if "ens_rd2022_aws" == compliance_framework:
            marcos = {}
            ens_compliance_table = {
                "Proveedor": [],
                "Marco/Categoria": [],
                "Estado": [],
                "Alto": [],
                "Medio": [],
                "Bajo": [],
                "Opcional": [],
                "Muted": [],
            }
            pass_count = []
            fail_count = []
            muted_count = []
            value_finding = 0
            for finding in findings:
                value_finding += 1
                check = bulk_checks_metadata[finding.check_metadata.CheckID]
                check_compliances = check.Compliance
                for compliance in check_compliances:
                    if (
                        compliance.Framework == "ENS"
                        and compliance.Provider == "AWS"
                        and compliance.Version == "RD2022"
                    ):
                        for requirement in compliance.Requirements:
                            for attribute in requirement.Attributes:
                                marco_categoria = (
                                    f"{attribute.Marco}/{attribute.Categoria}"
                                )
                                # Check if Marco/Categoria exists
                                if marco_categoria not in marcos:
                                    marcos[marco_categoria] = {
                                        "Estado": f"{Fore.GREEN}CUMPLE{Style.RESET_ALL}",
                                        "Opcional": 0,
                                        "Alto": 0,
                                        "Medio": 0,
                                        "Bajo": 0,
                                        "Muted": 0,
                                    }
                                if finding.muted and value_finding not in muted_count:
                                    muted_count.append(value_finding)
                                    marcos[marco_categoria]["Muted"] += 1
                                else:
                                    if finding.status == "FAIL":
                                        if (
                                            attribute.Tipo != "recomendacion"
                                            and value_finding not in fail_count
                                        ):
                                            fail_count.append(value_finding)
                                        marcos[marco_categoria][
                                            "Estado"
                                        ] = f"{Fore.RED}NO CUMPLE{Style.RESET_ALL}"
                                    elif (
                                        finding.status == "PASS"
                                        and value_finding not in pass_count
                                    ):
                                        pass_count.append(value_finding)
                                if attribute.Nivel == "opcional":
                                    marcos[marco_categoria]["Opcional"] += 1
                                elif attribute.Nivel == "alto":
                                    marcos[marco_categoria]["Alto"] += 1
                                elif attribute.Nivel == "medio":
                                    marcos[marco_categoria]["Medio"] += 1
                                elif attribute.Nivel == "bajo":
                                    marcos[marco_categoria]["Bajo"] += 1

            # Add results to table
            for marco in sorted(marcos):
                ens_compliance_table["Proveedor"].append(compliance.Provider)
                ens_compliance_table["Marco/Categoria"].append(marco)
                ens_compliance_table["Estado"].append(marcos[marco]["Estado"])
                ens_compliance_table["Opcional"].append(
                    f"{Fore.BLUE}{marcos[marco]['Opcional']}{Style.RESET_ALL}"
                )
                ens_compliance_table["Alto"].append(
                    f"{Fore.LIGHTRED_EX}{marcos[marco]['Alto']}{Style.RESET_ALL}"
                )
                ens_compliance_table["Medio"].append(
                    f"{orange_color}{marcos[marco]['Medio']}{Style.RESET_ALL}"
                )
                ens_compliance_table["Bajo"].append(
                    f"{Fore.YELLOW}{marcos[marco]['Bajo']}{Style.RESET_ALL}"
                )
                ens_compliance_table["Muted"].append(
                    f"{orange_color}{marcos[marco]['Muted']}{Style.RESET_ALL}"
                )
            if (
                len(fail_count) + len(pass_count) + len(muted_count) > 1
            ):  # If there are no resources, don't print the compliance table
                print(
                    f"\nEstado de Cumplimiento de {Fore.YELLOW}{compliance_framework.upper()}{Style.RESET_ALL}:"
                )
                overview_table = [
                    [
                        f"{Fore.RED}{round(len(fail_count) / len(findings) * 100, 2)}% ({len(fail_count)}) NO CUMPLE{Style.RESET_ALL}",
                        f"{Fore.GREEN}{round(len(pass_count) / len(findings) * 100, 2)}% ({len(pass_count)}) CUMPLE{Style.RESET_ALL}",
                        f"{orange_color}{round(len(muted_count) / len(findings) * 100, 2)}% ({len(muted_count)}) MUTED{Style.RESET_ALL}",
                    ]
                ]
                print(tabulate(overview_table, tablefmt="rounded_grid"))
                if not compliance_overview:
                    print(
                        f"\nResultados de {Fore.YELLOW}{compliance_framework.upper()}{Style.RESET_ALL}:"
                    )
                    print(
                        tabulate(
                            ens_compliance_table,
                            headers="keys",
                            tablefmt="rounded_grid",
                        )
                    )
                    print(
                        f"{Style.BRIGHT}* Solo aparece el Marco/Categoria que contiene resultados.{Style.RESET_ALL}"
                    )
                    print(
                        f"\nResultados detallados de {compliance_framework.upper()} en:"
                    )
                    print(
                        f" - CSV: {output_directory}/compliance/{output_filename}_{compliance_framework}.csv\n"
                    )
        elif "cis_" in compliance_framework:
            sections = {}
            cis_compliance_table = {
                "Provider": [],
                "Section": [],
                "Level 1": [],
                "Level 2": [],
                "Muted": [],
            }
            pass_count = []
            fail_count = []
            muted_count = []
            value_finding = 0
            for finding in findings:
                value_finding += 1
                check = bulk_checks_metadata[finding.check_metadata.CheckID]
                check_compliances = check.Compliance
                for compliance in check_compliances:
                    if (
                        compliance.Framework == "CIS"
                        and compliance.Version in compliance_framework
                    ):
                        for requirement in compliance.Requirements:
                            for attribute in requirement.Attributes:
                                section = attribute.Section
                                # Check if Section exists
                                if section not in sections:
                                    sections[section] = {
                                        "Status": f"{Fore.GREEN}PASS{Style.RESET_ALL}",
                                        "Level 1": {"FAIL": 0, "PASS": 0},
                                        "Level 2": {"FAIL": 0, "PASS": 0},
                                        "Muted": 0,
                                    }
                                if finding.muted and value_finding not in muted_count:
                                    muted_count.append(value_finding)
                                    sections[section]["Muted"] += 1
                                else:
                                    if (
                                        finding.status == "FAIL"
                                        and value_finding not in fail_count
                                    ):
                                        fail_count.append(value_finding)
                                    elif (
                                        finding.status == "PASS"
                                        and value_finding not in pass_count
                                    ):
                                        pass_count.append(value_finding)
                                if "Level 1" in attribute.Profile:
                                    if not finding.muted:
                                        if finding.status == "FAIL":
                                            sections[section]["Level 1"]["FAIL"] += 1
                                        else:
                                            sections[section]["Level 1"]["PASS"] += 1
                                elif "Level 2" in attribute.Profile:
                                    if not finding.muted:
                                        if finding.status == "FAIL":
                                            sections[section]["Level 2"]["FAIL"] += 1
                                        else:
                                            sections[section]["Level 2"]["PASS"] += 1

            # Add results to table
            sections = dict(sorted(sections.items()))
            for section in sections:
                cis_compliance_table["Provider"].append(compliance.Provider)
                cis_compliance_table["Section"].append(section)
                if sections[section]["Level 1"]["FAIL"] > 0:
                    cis_compliance_table["Level 1"].append(
                        f"{Fore.RED}FAIL({sections[section]['Level 1']['FAIL']}){Style.RESET_ALL}"
                    )
                else:
                    cis_compliance_table["Level 1"].append(
                        f"{Fore.GREEN}PASS({sections[section]['Level 1']['PASS']}){Style.RESET_ALL}"
                    )
                if sections[section]["Level 2"]["FAIL"] > 0:
                    cis_compliance_table["Level 2"].append(
                        f"{Fore.RED}FAIL({sections[section]['Level 2']['FAIL']}){Style.RESET_ALL}"
                    )
                else:
                    cis_compliance_table["Level 2"].append(
                        f"{Fore.GREEN}PASS({sections[section]['Level 2']['PASS']}){Style.RESET_ALL}"
                    )
                cis_compliance_table["Muted"].append(
                    f"{orange_color}{sections[section]['Muted']}{Style.RESET_ALL}"
                )
            if (
                len(fail_count) + len(pass_count) + len(muted_count) > 1
            ):  # If there are no resources, don't print the compliance table
                print(
                    f"\nCompliance Status of {Fore.YELLOW}{compliance_framework.upper()}{Style.RESET_ALL} Framework:"
                )
                overview_table = [
                    [
                        f"{Fore.RED}{round(len(fail_count) / len(findings) * 100, 2)}% ({len(fail_count)}) FAIL{Style.RESET_ALL}",
                        f"{Fore.GREEN}{round(len(pass_count) / len(findings) * 100, 2)}% ({len(pass_count)}) PASS{Style.RESET_ALL}",
                        f"{orange_color}{round(len(muted_count) / len(findings) * 100, 2)}% ({len(muted_count)}) MUTED{Style.RESET_ALL}",
                    ]
                ]
                print(tabulate(overview_table, tablefmt="rounded_grid"))
                if not compliance_overview:
                    print(
                        f"\nFramework {Fore.YELLOW}{compliance_framework.upper()}{Style.RESET_ALL} Results:"
                    )
                    print(
                        tabulate(
                            cis_compliance_table,
                            headers="keys",
                            tablefmt="rounded_grid",
                        )
                    )
                    print(
                        f"{Style.BRIGHT}* Only sections containing results appear.{Style.RESET_ALL}"
                    )
                    print(
                        f"\nDetailed results of {compliance_framework.upper()} are in:"
                    )
                    print(
                        f" - CSV: {output_directory}/compliance/{output_filename}_{compliance_framework}.csv\n"
                    )
        elif "mitre_attack" in compliance_framework:
            tactics = {}
            mitre_compliance_table = {
                "Provider": [],
                "Tactic": [],
                "Status": [],
                "Muted": [],
            }
            pass_count = []
            fail_count = []
            muted_count = []
            value_finding = 0
            for finding in findings:
                value_finding += 1
                check = bulk_checks_metadata[finding.check_metadata.CheckID]
                check_compliances = check.Compliance
                for compliance in check_compliances:
                    if (
                        "MITRE-ATTACK" in compliance.Framework
                        and compliance.Version in compliance_framework
                    ):
                        for requirement in compliance.Requirements:
                            for tactic in requirement.Tactics:
                                if tactic not in tactics:
                                    tactics[tactic] = {"FAIL": 0, "PASS": 0, "Muted": 0}
                                if finding.muted:
                                    if value_finding not in muted_count:
                                        muted_count.append(value_finding)
                                    tactics[tactic]["Muted"] += 1
                                else:
                                    if finding.status == "FAIL":
                                        if value_finding not in fail_count:
                                            fail_count.append(value_finding)
                                        tactics[tactic]["FAIL"] += 1
                                    elif finding.status == "PASS":
                                        if value_finding not in pass_count:
                                            pass_count.append(value_finding)
                                        tactics[tactic]["PASS"] += 1
            # Add results to table
            tactics = dict(sorted(tactics.items()))
            for tactic in tactics:
                mitre_compliance_table["Provider"].append(compliance.Provider)
                mitre_compliance_table["Tactic"].append(tactic)
                if tactics[tactic]["FAIL"] > 0:
                    mitre_compliance_table["Status"].append(
                        f"{Fore.RED}FAIL({tactics[tactic]['FAIL']}){Style.RESET_ALL}"
                    )
                else:
                    mitre_compliance_table["Status"].append(
                        f"{Fore.GREEN}PASS({tactics[tactic]['PASS']}){Style.RESET_ALL}"
                    )
                if tactics[tactic]["Muted"] > 0:
                    mitre_compliance_table["Muted"].append(
                        f"{orange_color}{tactics[tactic]['Muted']}{Style.RESET_ALL}"
                    )
            if (
                len(fail_count) + len(pass_count) + len(muted_count) > 1
            ):  # If there are no resources, don't print the compliance table
                print(
                    f"\nCompliance Status of {Fore.YELLOW}{compliance_framework.upper()}{Style.RESET_ALL} Framework:"
                )
                overview_table = [
                    [
                        f"{Fore.RED}{round(len(fail_count) / len(findings) * 100, 2)}% ({len(fail_count)}) FAIL{Style.RESET_ALL}",
                        f"{Fore.GREEN}{round(len(pass_count) / len(findings) * 100, 2)}% ({len(pass_count)}) PASS{Style.RESET_ALL}",
                        f"{orange_color}{round(len(muted_count) / len(findings) * 100, 2)}% ({len(muted_count)}) MUTED{Style.RESET_ALL}",
                    ]
                ]
                print(tabulate(overview_table, tablefmt="rounded_grid"))
                if not compliance_overview:
                    print(
                        f"\nFramework {Fore.YELLOW}{compliance_framework.upper()}{Style.RESET_ALL} Results:"
                    )
                    print(
                        tabulate(
                            mitre_compliance_table,
                            headers="keys",
                            tablefmt="rounded_grid",
                        )
                    )
                    print(
                        f"{Style.BRIGHT}* Only sections containing results appear.{Style.RESET_ALL}"
                    )
                    print(
                        f"\nDetailed results of {compliance_framework.upper()} are in:"
                    )
                    print(
                        f" - CSV: {output_directory}/compliance/{output_filename}_{compliance_framework}.csv\n"
                    )
        else:
            pass_count = []
            fail_count = []
            muted_count = []
            value_finding = 0
            for finding in findings:
                value_finding += 1
                check = bulk_checks_metadata[finding.check_metadata.CheckID]
                check_compliances = check.Compliance
                for compliance in check_compliances:
                    if (
                        compliance.Framework.upper()
                        in compliance_framework.upper().replace("_", "-")
                        and compliance.Version in compliance_framework.upper()
                        and compliance.Provider in compliance_framework.upper()
                    ):
                        for requirement in compliance.Requirements:
                            for attribute in requirement.Attributes:
                                if finding.muted and value_finding not in muted_count:
                                    muted_count.append(value_finding)
                                else:
                                    if (
                                        finding.status == "FAIL"
                                        and value_finding not in fail_count
                                    ):
                                        fail_count.append(value_finding)
                                    elif (
                                        finding.status == "PASS"
                                        and value_finding not in pass_count
                                    ):
                                        pass_count.append(value_finding)
            if (
                len(fail_count) + len(pass_count) + len(muted_count) > 1
            ):  # If there are no resources, don't print the compliance table
                print(
                    f"\nCompliance Status of {Fore.YELLOW}{compliance_framework.upper()}{Style.RESET_ALL} Framework:"
                )
                overview_table = [
                    [
                        f"{Fore.RED}{round(len(fail_count) / len(findings) * 100, 2)}% ({len(fail_count)}) FAIL{Style.RESET_ALL}",
                        f"{Fore.GREEN}{round(len(pass_count) / len(findings) * 100, 2)}% ({len(pass_count)}) PASS{Style.RESET_ALL}",
                        f"{orange_color}{round(len(muted_count) / len(findings) * 100, 2)}% ({len(muted_count)}) MUTED{Style.RESET_ALL}",
                    ]
                ]
                print(tabulate(overview_table, tablefmt="rounded_grid"))
            if not compliance_overview:
                print(f"\nDetailed results of {compliance_framework.upper()} are in:")
                print(
                    f" - CSV: {output_directory}/compliance/{output_filename}_{compliance_framework}.csv\n"
                )
    except Exception as error:
        logger.critical(
            f"{error.__class__.__name__}:{error.__traceback__.tb_lineno} -- {error}"
        )
        sys.exit(1)


def get_check_compliance(finding, provider_type, output_options) -> dict:
    """get_check_compliance returns a map with the compliance framework as key and the requirements where the finding's check is present.

        Example:

    {
        "CIS-1.4": ["2.1.3"],
        "CIS-1.5": ["2.1.3"],
    }
    """
    try:
        check_compliance = {}
        # We have to retrieve all the check's compliance requirements
        if finding.check_metadata.CheckID in output_options.bulk_checks_metadata:
            for compliance in output_options.bulk_checks_metadata[
                finding.check_metadata.CheckID
            ].Compliance:
                compliance_fw = compliance.Framework
                if compliance.Version:
                    compliance_fw = f"{compliance_fw}-{compliance.Version}"
                if compliance.Provider == provider_type.upper():
                    if compliance_fw not in check_compliance:
                        check_compliance[compliance_fw] = []
                    for requirement in compliance.Requirements:
                        check_compliance[compliance_fw].append(requirement.Id)
        return check_compliance
    except Exception as error:
        logger.critical(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}] -- {error}"
        )
        sys.exit(1)
