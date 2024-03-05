import importlib

# TODO: remove after fixing tests
# import sys
# from dataclasses import dataclass
# from os import makedirs
# from os.path import isdir

# from prowler.lib.logger import logger


# TODO: remove after fixing tests
# def set_provider_output_options(
#     provider: str, arguments, identity, mutelist_file, bulk_checks_metadata
# ):
#     """
#     set_provider_output_options configures automatically the outputs based on the selected provider and returns the Provider_Output_Options object.
#     """
#     try:
#         # Dynamically load the Provider_Output_Options class
#         provider_output_class = f"{provider.capitalize()}_Output_Options"
#         provider_output_options = getattr(
#             importlib.import_module(__name__), provider_output_class
#         )(arguments, identity, mutelist_file, bulk_checks_metadata)
#     except Exception as error:
#         logger.critical(
#             f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
#         )
#         sys.exit(1)
#     else:
#         return provider_output_options


# TODO: review this function, probably is not needed anymore
def get_provider_output_model(provider_type):
    """
    get_provider_output_model returns the model <provider>_Check_Output_CSV for each provider
    """
    # TODO: classes should be AwsCheckOutputCSV
    output_provider_model_name = f"{provider_type.capitalize()}_Check_Output_CSV"
    output_provider_models_path = "prowler.lib.outputs.models"
    output_provider_model = getattr(
        importlib.import_module(output_provider_models_path), output_provider_model_name
    )

    return output_provider_model


# TODO: remove after fixing tests
# @dataclass
# class Provider_Output_Options:
#     status: bool
#     output_modes: list
#     output_directory: str
#     mutelist_file: str
#     bulk_checks_metadata: dict
#     verbose: str
#     output_filename: str
#     only_logs: bool
#     unix_timestamp: bool

#     def __init__(self, arguments, mutelist_file, bulk_checks_metadata):
#         self.status = arguments.status
#         self.output_modes = arguments.output_modes
#         self.output_directory = arguments.output_directory
#         self.verbose = arguments.verbose
#         self.bulk_checks_metadata = bulk_checks_metadata
#         self.mutelist_file = mutelist_file
#         self.only_logs = arguments.only_logs
#         self.unix_timestamp = arguments.unix_timestamp
#         # Check output directory, if it is not created -> create it
#         if arguments.output_directory:
#             if not isdir(arguments.output_directory):
#                 if arguments.output_modes:
#                     makedirs(arguments.output_directory, exist_ok=True)
#             if not isdir(arguments.output_directory + "/compliance"):
#                 if arguments.output_modes:
#                     makedirs(arguments.output_directory + "/compliance", exist_ok=True)
