# ===============================================================================
# Created:        11 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Library to implement Anaplan API to get lists of model resources, upload files to Anaplan server,
#                 download files from Anaplan server, and execute actions.
# ===============================================================================
import json
import logging
import os
import requests
from typing import List
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .AnaplanConnection import AnaplanConnection
from .ParserResponse import ParserResponse
from .ImportParser import ImportParser
from .ExportParser import ExportParser
from .ActionParser import ActionParser
from .ProcessParser import ProcessParser
from .BasicAuthentication import BasicAuthentication
from .CertificateAuthentication import CertificateAuthentication
from .FileUpload import FileUpload
from .FileDownload import FileDownload
from .StreamUpload import StreamUpload
from .ActionTask import ActionTask
from .ImportTask import ImportTask
from .ExportTask import ExportTask
from .ProcessTask import ProcessTask
from .Resources import Resources
from .ResourceParserList import ResourceParserList
from .AnaplanResourceList import AnaplanResource

# ===============================================================================
# Defining global variables
# ===============================================================================
__base_url__ = "https://api.anaplan.com/2/0/workspaces"
__post_body__ = {
    "localeName": "en_US"
}

logger = logging.getLogger(__name__)


# ===========================================================================
# This function reads the authentication type, Basic or Certificate, then passes
# the remaining variables to anaplan_auth to generate the authorization for Anaplan API
# ===========================================================================
def generate_authorization(auth_type, *args):
    """
    :param auth_type
    :param args: Path to public certificate, and private key if auth_type='certificate'; Anaplan Username,
    Anaplan Password, and private key if auth_type='basic'
    :returns: Header Authentication value, and token expiry in epoch
    """

    if auth_type.lower() == 'basic':
        basic = BasicAuthentication()
        header_string = basic.auth_header(args[0], args[1])
        authorization = basic.authenticate(basic.auth_request(header_string))
        return authorization
    elif auth_type.lower() == 'certificate':
        cert_auth = CertificateAuthentication()

        cert = args[0]
        priv_key = args[1]

        header_string = cert_auth.auth_header(cert)
        post_data = cert_auth.generate_post_data(priv_key)
        authorization = cert_auth.authenticate(cert_auth.auth_request(header_string, post_data))
    else:
        logger.error("Please enter a valid authentication method: Basic or Certificate")
        return None

    if authorization[0]:
        auth_token = authorization[0]
        if not auth_token[:5] == "Error":
            return authorization
        else:
            logger.error(f"Authentication Failed: {auth_token}")


def file_upload(conn: AnaplanConnection, file_id: str, chunk_size: int, data: str):
    """
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param file_id: ID of the file in Anaplan
    :param chunk_size: Desired chunk size of the upload request between 1-50
    :param data: Data to load, either path to local file or string
    :return: None
    """

    if os.path.isfile(data):
        upload = FileUpload(conn, file_id)
        upload.upload(chunk_size, data)
    else:
        upload = StreamUpload(conn, file_id)
        upload.upload(chunk_size, data)


def execute_action(conn: AnaplanConnection, action_id: str, retry_count: int, mapping_params: dict = None) \
        -> List[ParserResponse]:
    factories = {
        "117": ActionTask,
        "112": ImportTask,
        "116": ExportTask,
        "118": ProcessTask
    }

    if action_id[:3] in factories:
        factory = factories[action_id[:3]]

        action = factory.get_action(conn, action_id, retry_count, mapping_params)
        task = action.execute()
        parser = factory.get_parser(conn, task[0], task[1])
        task_results = parser.get_results()

        return task_results


# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
def parse_task_response(conn, results, url, action_id):
    """
    :param conn: Anaplan connection object
    :param results: JSON dump of the results of an Anaplan action
    :param url: URL of anaplan task
    :param action_id: ID of the Anaplan action
    :returns: String with task details, array of error dump dataframes
    """

    if action_id[:3] == "112":
        # Import
        return ImportParser(results, url)
    elif action_id[:3] == "116":
        # Export
        return ExportParser(conn, results, url)
    elif action_id[:3] == "117":
        # Action
        return ActionParser(results, url)
    elif action_id[:3] == "118":
        # Process
        return ProcessParser(conn, results, url)


# ===========================================================================
# This function queries the Anaplan model for a list of the desired resources:
# files, actions, imports, exports, processes and returns the JSON response.
# ===========================================================================
def get_list(conn: AnaplanConnection, resource: str) -> AnaplanResource:
    """
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param resource: The Anaplan model resource to be queried and returned to the user
    """

    resources = Resources(conn, resource)
    resources_list = resources.get_resources()
    resource_parser = ResourceParserList()
    return resource_parser.get_parser(resources_list)


# ===========================================================================
# This function downloads a file from Anaplan to the specified path.
# ===========================================================================
def get_file(conn, file_id):
    """
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param file_id: ID of the Anaplan file to download
    """

    file_download = FileDownload(conn, file_id)
    return file_download.download_file()
