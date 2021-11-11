# ===============================================================================
# Created:        11 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Library to implement Anaplan API to get lists of model resources, upload files to Anaplan server,
#                 download files from Anaplan server, and execute actions.
# ===============================================================================
import logging
from typing import List, Union
from .AnaplanConnection import AnaplanConnection
from .ParserResponse import ParserResponse
from .BasicAuthentication import BasicAuthentication
from .CertificateAuthentication import CertificateAuthentication
from .FileDownload import FileDownload
from .TaskFactoryGenerator import TaskFactoryGenerator
from .Resources import Resources
from .ResourceParserList import ResourceParserList
from .AnaplanResourceList import AnaplanResource
from .AuthToken import AuthToken
from .UploadFactory import UploadFactory

logger = logging.getLogger(__name__)


# ===========================================================================
# This function reads the authentication type, Basic or Certificate, then passes
# the remaining variables to anaplan_auth to generate the authorization for Anaplan API
# ===========================================================================
def generate_authorization(auth_type: str = "Basic", email: str = None, password: str = None,
                           private_key: Union[bytes, str] = None, cert: Union[bytes, str] = None) -> AuthToken:
    """
    :param auth_type: Basic or Certificate authentication
    :param email: Anaplan email address for Basic auth
    :param password: Anaplan password for Basic auth
    :param private_key: Private key string or path to key file
    :param cert: Public certificate string or path to file
    :return:
    """

    if auth_type.lower() == 'basic' and email and password:
        basic = BasicAuthentication()
        header_string = basic.auth_header(email, password)
        return basic.authenticate(basic.auth_request(header_string))
    elif auth_type.lower() == 'certificate' and cert and private_key:
        cert_auth = CertificateAuthentication()
        header_string = cert_auth.auth_header(cert)
        post_data = cert_auth.generate_post_data(private_key)
        return cert_auth.authenticate(cert_auth.auth_request(header_string, post_data))
    else:
        logger.error(f"Invalid authentication method: {auth_type}")
        raise ValueError(f"Invalid authentication method: {auth_type}")


def file_upload(conn: AnaplanConnection, file_id: str, chunk_size: int, data: str) -> None:
    """
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param file_id: ID of the file in Anaplan
    :param chunk_size: Desired chunk size of the upload request between 1-50
    :param data: Data to load, either path to local file or string
    :return: None
    """

    file = UploadFactory(data)
    uploader = file.get_uploader(conn, file_id)
    uploader.upload(chunk_size, data)


def execute_action(conn: AnaplanConnection, action_id: str, retry_count: int, mapping_params: dict = None) \
        -> List[ParserResponse]:

    generator = TaskFactoryGenerator(action_id[:3])
    factory = generator.get_factory()

    action = factory.get_action(conn, action_id, retry_count, mapping_params)
    task = action.execute()
    parser = factory.get_parser(conn, task[0], task[1])
    task_results = parser.get_results()

    return task_results


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
def get_file(conn: AnaplanConnection, file_id: str) -> str:
    """
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param file_id: ID of the Anaplan file to download
    """

    file_download = FileDownload(conn, file_id)
    return file_download.download_file()
