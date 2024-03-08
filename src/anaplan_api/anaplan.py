# ===============================================================================
# Created:        11 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Library to implement Anaplan API to get lists of model resources, upload files to Anaplan server,
#                 download files from Anaplan server, and execute actions.
# ===============================================================================
from __future__ import annotations
import logging
from typing import List, Union, TYPE_CHECKING
from .BasicAuthentication import BasicAuthentication
from .CertificateAuthentication import CertificateAuthentication
from .UploadFactory import UploadFactory
from .TaskFactoryGenerator import TaskFactoryGenerator
from .Resources import Resources
from .ResourceParserList import ResourceParserList
from .FileDownload import FileDownload
from .AuthToken import AuthToken
from .util.Util import InvalidAuthenticationError

if TYPE_CHECKING:
    from .AnaplanConnection import AnaplanConnection
    from .ParserResponse import ParserResponse
    from .AnaplanResourceList import AnaplanResource

logger = logging.getLogger(__name__)


# ===========================================================================
# This function reads the authentication type, Basic or Certificate, then passes
# the remaining variables to anaplan_auth to generate the authorization for Anaplan API
# ===========================================================================
def generate_authorization(
    auth_type: str = "Basic",
    email: str = None,
    password: str = None,
    private_key: Union[bytes, str] = None,
    cert: Union[bytes, str] = None,
) -> AuthToken:
    """Generate an Anaplan AuthToken object

    :param auth_type: Basic or Certificate authentication
    :param email: Anaplan email address for Basic auth
    :param password: Anaplan password for Basic auth
    :param private_key: Private key string or path to key file
    :param cert: Public certificate string or path to file
    :return: AnaplanAuthToken value and expiry time in epoch
    :rtype: AuthToken
    """

    if auth_type.lower() == "basic" and email and password:
        basic = BasicAuthentication()
        header_string = basic.auth_header(email, password)
        token, expiry = basic.authenticate(basic.auth_request(header_string))
        return AuthToken(token, expiry)
    elif auth_type.lower() == "certificate" and cert and private_key:
        cert_auth = CertificateAuthentication()
        header_string = cert_auth.auth_header(cert)
        post_data = cert_auth.generate_post_data(private_key)
        token, expiry = cert_auth.authenticate(cert_auth.auth_request(header_string, post_data))
        return AuthToken(token, expiry)
    else:
        if (email and password) or (cert and private_key):
            logger.error(f"Invalid authentication method: {auth_type}")
            raise InvalidAuthenticationError(
                f"Invalid authentication method: {auth_type}"
            )
        else:
            logger.error(
                "Email address and password or certificate and key must not be blank"
            )
            raise InvalidAuthenticationError(
                "Email address and password or certificate and key must not be blank"
            )


def file_upload(
    conn: AnaplanConnection, file_id: str, chunk_size: int, data: str
) -> None:
    """Upload a file to Anaplan model

    :param conn: AnaplanConnection object which contains AuthToken object, workspace ID, and model ID
    :param file_id: ID of the file in Anaplan
    :param chunk_size: Desired chunk size of the upload request between 1-50
    :param data: Data to load, either path to local file or string
    """

    file = UploadFactory(data)
    uploader = file.get_uploader(conn, file_id)
    uploader.upload(chunk_size, data)


def execute_action(
    conn: AnaplanConnection,
    action_id: str,
    retry_count: int,
    mapping_params: dict = None,
) -> List[ParserResponse]:
    """Execute a specified Anaplan action

    :param conn: AnaplanConnection object which contains AuthToken object, workspace ID, and model ID
    :param action_id: ID of the Anaplan action to execute
    :param retry_count: Number of times to attempt to retry if an error occurs executing an action
    :param mapping_params: Optional dictionary of import mapping parameters
    :return: Detailed results of the requested action task.
    :rtype: List[ParserResponse]
    """

    generator = TaskFactoryGenerator(action_id[:3])
    factory = generator.get_factory()

    action = factory.get_action(
        conn=conn,
        action_id=action_id,
        retry_count=retry_count,
        mapping_params=mapping_params,
    )
    task = action.execute()
    parser = factory.get_parser(
        conn=conn, results=task.results, url=task.url
    )
    task_results = parser.get_results()

    return task_results


# ===========================================================================
# This function queries the Anaplan model for a list of the desired resources:
# files, actions, imports, exports, processes and returns the JSON response.
# ===========================================================================
def get_list(conn: AnaplanConnection, resource: str) -> AnaplanResource:
    """Get list of the specified resource in the Anaplan model

    :param conn: AnaplanConnection object which contains AuthToken object, workspace ID, and model ID
    :type conn: AnaplanConnection
    :param resource: The Anaplan model resource to be queried and returned to the user
    :type resource: str
    :return: Detailed list of the requested resource
    :rtype: AnaplanResource
    """

    resources = Resources(conn=conn, resource=resource)
    resources_list = resources.get_resources()
    resource_parser = ResourceParserList()
    return resource_parser.get_parser(resources_list)


# ===========================================================================
# This function downloads a file from Anaplan to the specified path.
# ===========================================================================
def get_file(conn: AnaplanConnection, file_id: str) -> str:
    """Download the specified file from the Anaplan model

    :param conn: AnaplanConnection object which contains AuthToken object, workspace ID, and model ID
    :type conn: AnaplanConnection
    :param file_id: ID of the Anaplan file to download
    :type file_id: str
    :return: File data from anaplan
    :rtype: str
    """

    file_download = FileDownload(conn=conn, file_id=file_id)
    return file_download.download_file()
