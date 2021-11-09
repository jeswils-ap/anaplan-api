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
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .AnaplanConnection import AnaplanConnection
from .ImportParser import ImportParser
from .ExportParser import ExportParser
from .ActionParser import ActionParser
from .ProcessParser import ProcessParser
from .BasicAuthentication import BasicAuthentication
from .CertificateAuthentication import CertificateAuthentication
from .FileUpload import FileUpload
from .FileDownload import FileDownload
from .StreamUpload import StreamUpload
from .ParameterAction import ParameterAction
from .ActionTask import ActionTask
from .ImportTask import ImportTask
from .ExportTask import ExportTask
from .ProcessTask import ProcessTask

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


def execute_action(conn: AnaplanConnection, action_id: str, retry_count: int, mapping_params: dict = None):
    factories = {
        "117": ActionTask,
        "112": ImportTask,
        "116": ExportTask,
        "118": ProcessTask
    }

    if not mapping_params:
        if action_id[:3] in factories:
            factory = factories[action_id[:3]]
            action = factory.get_action(conn, action_id, retry_count)
            task = action.execute()
            parser = factory.get_parser(conn, task[0], task[1])
            task_results = parser.get_results()
            return task_results
    else:
        task = ParameterAction(conn, action_id, retry_count, mapping_params)
        task_details = task.execute()
        return parse_task_response(conn, task_details[0], task_details[1], action_id)


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
def get_list(conn, resource):
    """
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param resource: The Anaplan model resource to be queried and returned to the user
    """

    authorization = conn.get_auth()
    workspace_guid = conn.get_workspace()
    model_guid = conn.get_model()
    response = {}

    get_header = {
        'Authorization': authorization,
        'Content-Type': 'application/json'
    }

    url = ''.join([__base_url__, "/", workspace_guid, "/models/", model_guid, "/", resource.lower()])

    logger.debug(f"Fetching {resource}")
    try:
        response = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
    except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
        logger.error(f"Error fetching resource {resource}, {e}")
    logger.debug(f"Finished fetching {resource}")

    return response[resource]


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


# ===============================================================================
# This function queries the model for name and chunk count of a specified file
# ===============================================================================
def get_file_details(conn, file_id):
    """
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param file_id: ID of the Anaplan file to download
    """

    chunk_count = 0
    file_name = ""
    files_list = {}

    authorization = conn.get_auth()
    workspace_guid = conn.get_workspace()
    model_guid = conn.get_model()

    get_header = {
        "Authorization": authorization,
    }

    url = ''.join([__base_url__, "/", workspace_guid, "/models/", model_guid, "/files/"])

    try:
        files_list = requests.get(url, headers=get_header, timeout=(5, 30))
    except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
        logger.error(f"Error getting details for {file_id}, {e}")

    if files_list.ok:
        logger.debug("Fetching file details.")
        files = json.loads(files_list.text)
        files = files['files']
        for item in files:
            temp_id = str(item['id'])
            chunk_count = item['chunkCount']
            file_name = str(item['name'])
            if temp_id == file_id:
                logger.debug("Finished fetching file details.")
                break

    return [chunk_count, file_name]


# ===============================================================================
# This function returns the user's Anaplan ID
# ===============================================================================
def get_user_id(conn):
    """
    @param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    """

    user_details = {}
    user_id = {}
    url = 'https://api.anaplan.com/2/0/users/me'

    authorization = conn.get_auth()

    get_header = {
        "Authorization": authorization
    }

    logger.debug("Fetching user ID...")

    try:
        logger.debug("Retrieving details of current user.")
        user_details = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
    except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
        logger.error(f"Error fetching user details {e}")
    except ValueError as e:
        logger.error(f"Error loading user details {e}")
    if 'user' in user_details:
        if 'id' in user_details['user']:
            user_id = user_details['user']['id']

    return user_id


# ===============================================================================
# This function queries Anaplan for a list of models the designated user has
# access to and returns this as a JSON array.
# ===============================================================================
def get_models(conn, user_id):
    """
    @param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    @param user_id: 32-character string that uniquely identifies the Anaplan user
    """

    model_list = {}
    url = ''.join(["https://api.anaplan.com/2/0/users/", str(user_id), "/models"])
    authorization = conn.get_auth()

    get_header = {
        "Authorization": authorization,
        "Content-Type": "application/json"
    }

    logger.debug("Fetching models")

    try:
        model_list = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
    except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
        logger.error(f"Error getting models list: {e}")
    except ValueError as e:
        logger.error(f"Error loading model list {e}")

    if 'models' in model_list:
        models = model_list['models']
        logger.debug("Finished fetching models.")
        return models
    else:
        raise AttributeError("Models not found in response.")


# ===============================================================================
# This function returns the list of Anaplan workspaces a user may access as a
# JSON array
# ===============================================================================
def get_workspaces(conn, user_id):
    """
    @param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    @param user_id: 32-character string that uniquely identifies the Anaplan user
    """

    workspace_list = {}
    url = ''.join(["https://api.anaplan.com/2/0/users/", str(user_id), "/workspaces"])
    authorization = conn.get_auth()

    get_header = {
        "Authorization": authorization,
        "Content-Type": "application/json"
    }

    logger.debug("Fetching workspaces.")

    try:
        workspace_list = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
    except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
        logger.error(f"Error getting workspace list: {e}")
    except ValueError as e:
        logger.error(f"Error loading workspace list {e}")

    if 'workspaces' in workspace_list:
        workspaces = workspace_list['workspaces']
        logger.debug("Finished fetching workspaces.")
        return workspaces
    else:
        raise AttributeError("Workspace not found in response.")
