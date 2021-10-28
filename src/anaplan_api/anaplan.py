#===============================================================================
# Created:        11 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    This library implements the Anaplan API to get lists of model resources, upload files to Anaplan server, 
#                 download files from Anaplan server, and execute actions.
#===============================================================================

import requests
import json
import os
import logging
from anaplan_api import anaplan_cert_auth, anaplan_basic_auth, import_parser, export_parser, action_parser, process_parser, file_upload, streaming_upload
from time import sleep

#===============================================================================
# Defining global variables
#===============================================================================
__base_url__ = "https://api.anaplan.com/2/0/workspaces"
__post_body__ = {
            "localeName":"en_US"
        }

logger = logging.getLogger(__name__)

#===========================================================================
# This function reads the authentication type, Basic or Certificate, then passes
# the remaining variables to anaplan_auth to generate the authorization for Anaplan API
#===========================================================================
def generate_authorization(auth_type, *args):    
    '''
    :param auth_type: 
    :param *args: Path to public certificate, and private key if auth_type='certificate'; Anaplan Username, Anaplan 
                  Password, and private key if auth_type='basic'
    :returns: Header Authenication value, and token expiry in epoch
    '''
    
    if auth_type.lower() == 'basic':
        header_string = anaplan_basic_auth.auth_header(args[0], args[1])
        authorization = anaplan_basic_auth.authenticate(anaplan_basic_auth.auth_request(header_string))
        return authorization
    elif auth_type.lower() == 'certificate':
        privKey = args[0]
        pubCert = args[1]
        
        header_string = anaplan_cert_auth.auth_header(pubCert)
        post_data = anaplan_cert_auth.generate_post_data(privKey)
        authorization = anaplan_cert_auth.authenticate(anaplan_cert_auth.auth_request(header_string, post_data))
    else:
        logger.error("Please enter a valid authentication method: Basic or Certificate")
        return None
        
    if not authorization[:5] == "Error":
        return authorization   
    else:
        logger.error("Authentication Failed: {0}".format(authorization))
    

#===========================================================================
# This function reads a flat file of an arbitrary size and uploads to Anaplan
# in chunks of a size defined by the user.
#===========================================================================
def flat_file_upload(conn, fileId, chunkSize, file):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param fileId: ID of the file in the Anaplan model
    :param chunkSize: Desired size of the chunk, in megabytes
    :param file: Path to the local file to be uploaded to Anaplan
    '''
    file_upload.upload(conn, fileId, chunkSize, file)

#===========================================================================
# This function uploads a data stream to Anaplan in a chunk of no larger
# than 50mb. 
#===========================================================================
def stream_upload(conn, file_id, chunkSize, data):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param fileId: ID of the file in the Anaplan model
    :param buffer: data to uplaod to Anaplan file
    :param *args: Once complete, this should be True to complete upload and reset chunk counter
    '''

    streaming_upload.upload(conn, file_id, chunkSize, data)

#===========================================================================
# This function reads the ID of the desired action to run, POSTs the task
# to the Anaplan API to execute the action, then monitors the status until
# complete.
#===========================================================================
def execute_action(conn, actionId, retryCount):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param actionId: ID of the action in the Anaplan model
    :param retryCount: The number of times to attempt to retry the action if it fails
    '''
    
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    post_header = {
            'Authorization': authorization,
            'Content-Type':'application/json'
        }
    if actionId[2] == "2" or actionId[2] == "6" or actionId[2] == "7" or actionId[2] == "8":
        if actionId[2] == "2":
            url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/imports/", actionId, "/tasks"])
        elif actionId[2] == "6":
            url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/exports/", actionId, "/tasks"])
        elif actionId[2] == "7":
            url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/actions/", actionId, "/tasks"])
        elif actionId[2] == "8":
            url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/processes/", actionId, "/tasks"])

        logger.info("Running action {0}".format(actionId))
        taskId = run_action(url, post_header, retryCount)
        return check_status(conn, actionId, url, taskId, post_header)
    else:
        logger.error("Incorrect action ID provided!")
        return None

#===========================================================================
# This function reads the ID of the desired import or process to run with
# mapping parameters declared, POSTs the task to the Anaplan API to execute 
# the action, then monitors the status until complete.
#===========================================================================
def execute_action_with_parameters(conn, actionId, retryCount, **params):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param actionId: ID of the action in the Anaplan model
    :param retryCount: The number of times to attempt to retry the action if it fails
    '''
    
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    post_header = {
            'Authorization': authorization,
            'Content-Type':'application/json'
        }
    
    body = ""
    body_value = ""
    
    if len(params) > 1:
        for key, value in params.items():
            #body += "\"entityType:\"" + key + "\"" + ",\"entityType:\"" + value + "\"" + ","
            body.join("\"entityType:\"", key, "\"", ",\"entityType:\"", value, "\"", ",")
        body = body[:-1]
        #body_value = "[" + body + "]"
        body_value.join("[", body, "]")
    else:
        for key, value in params.items():
            #body += "[\"" + key + "\"" + ":" + "\"" + value + "\"]"
            body_value.join("[\"", key, "\"", ":", "\"", value, "\"]")
    
    
    post_body = {
                    "localeName":"en_US","mappingParameters": body
                }
    
    if actionId[2] == "2" or actionId[2] == "8":
        logger.info("Running action {0}".format(actionId))
        if actionId[2] == "2":
            url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/imports/", actionId, "/tasks"])
        elif actionId[2] == "8":
            url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/processes/", actionId, "/tasks"])
        taskId = run_action(url, post_header, retryCount, post_body)
        return check_status(conn, actionId, url, taskId, post_header)
    else:
        logger.error("Incorrect action ID provided! Only imports and processes may be executed with parameters.")
        return None

#===========================================================================
# This function executes the Anaplan action, if there is a server error it
# will wait, and retry a number of times defined by the user. Once the task
# is successfully created, the task ID is returned.
#===========================================================================
def run_action(url, post_header, retryCount):
    '''
    @param url: POST URL for Anaplan action
    @param post_header: Authorization header string
    @param retryCount: Number of times to retry executino of the action
    '''
    
    state = 0
    sleepTime = 10
        
    while True:
        try:
            run_action = requests.post(url, headers=post_header, json=__post_body__)
        except Exception as e:
            logger.error("Error running action {0}".format(e))
        if run_action.status_code != 200 and state < retryCount:
            sleep(sleepTime)
            state += 1
            sleepTime = sleepTime * 1.5
        else:
            break
    if state < retryCount:
        taskId = json.loads(run_action.text)
        if 'taskId' in taskId:
            return taskId["taskId"]

#===========================================================================
# This function monitors the status of Anaplan action. Once complete it returns
# the JSON text of the response.
#===========================================================================        
def check_status(conn, actionId, url, taskId, post_header):
    '''
    @param url: Anaplan task URL
    @param taskId: ID of the Anaplan task executed
    @param post_header: Authorization header value
    '''
    status = ""

    while True:
        try:
            get_status = json.loads(requests.get(''.join([url, "/", taskId]), headers=post_header).text)
        except Exception as e:
            logger.error("Error getting result for task {0}".format(e))
        if 'task' in get_status:
            if 'taskState' in get_status['task']:
                status = get_status["task"]["taskState"]
        if status == "COMPLETE":
            results = get_status["task"]
            break
        #Wait 1 seconds before continuing loop
        sleep(1)
    
    return parse_task_response(conn, actionId, results, url, taskId, post_header)
    
#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
def parse_task_response(conn, actionId, results, url, taskId, post_header):
    '''
    :param results: JSON dump of the results of an Anaplan action
    :returns: String with task details, array of error dump dataframes
    '''
    
    if actionId[:3] == "112":
        #Import
        return import_parser.parse_response(results, url, taskId, post_header)
    elif actionId[:3] == "116":
        #Export
        return export_parser.parse_response(conn, results, url, taskId, post_header)
    elif actionId[:3] == "117":
        #Action
        return action_parser.parse_response(results, url, taskId, post_header)
    elif actionId[:3] == "118":
        #Process
        return process_parser.parse_response(conn, results, url, taskId, post_header)

#===========================================================================
# This function queries the Anaplan model for a list of the desired resources:
# files, actions, imports, exports, processes and returns the JSON response.
#===========================================================================
def get_list(conn, resource):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param resource: The Anaplan model resource to be queried and returned to the user
    '''
    
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    get_header = {
            'Authorization': authorization,
            'Content-Type':'application/json'
    }
    url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/", resource.lower()])
    
    logger.debug("Fetching {0}".format(resource))
    
    try:
        response = requests.get(url, headers=get_header)
        response.raise_for_status()
    except Exception as e:
        logger.error("Error fetching resource {0}, {1}".format(resource, e))
    response = response.text
    response = json.loads(response)
    
    logger.debug("Finished fetching {0}".format(resource))
     
    return response[resource]

#===========================================================================
# This function reads the JSON response of the Anaplan resources, prints to screen.
#===========================================================================
def parse_get_response(response):
    '''
    :param response: JSON text of Anaplan model resources
    '''
    
    for item in response:
        if item == None:
            break
        else:
            logger.info("Name: {0}\nID: {1}\n".format(item["name"], item["id"]))
            
#===========================================================================
# This function downloads a file from Anaplan to the specified path.
#===========================================================================
def get_file(conn, fileId):
    ''' 
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param fileId: ID of the Anaplan file to download
    :param location: Location on the local machine where the download will be saved
    '''
    
    chunk = 0
    details = get_file_details(conn, fileId)
    chunk_count = details[0]
    file_name = details[1]
    
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    get_header = {
                "Authorization": authorization,
    }    
    
    url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/files/", fileId, "/chunks/"])

    logger.info("Starting download of file {0}".format(fileId))
    
    file = ""
    
    while int(chunk) < int(chunk_count):
        try:
            logger.debug("Downloading chunk {0}".format(chunk))
            file_contents = requests.get(''.join([url, str(chunk)]), headers=get_header)
            file_contents.raise_for_status()
        except Exception as e:
            logger.error("Error downloading chunk {0}".format(e))
        if file_contents.ok:
            logger.debug("Chunk {0} downloaded successfully.".format(chunk))
            file += file_contents.text
        else:
            logger.error("There was a problem downloading {0}".format(file_name))
            break
        chunk = str(int(chunk) + 1)
        
    if int(chunk) == int(chunk_count):
        logger.info("File download complete!")
        
    return file

#===============================================================================
# This function queries the model for name and chunk count of a specified file
#===============================================================================
def get_file_details(conn, fileId):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param fileId: ID of the Anaplan file to download
    '''
    
    chunkCount = 0
    file_name = ""
    
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    get_header = {
                "Authorization": authorization,
    }    
    
    url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/files/"])
    
    try:
        files_list = requests.get(url, headers=get_header)
        files_list.raise_for_status()
    except Exception as e:
        logger.error("Error getting details for {0}, {1}".format(fileId, e))
    
    if files_list.ok:
        logger.debug("Fetching file details.")
        files=json.loads(files_list.text)
        files=files["files"]
        for item in files:
            temp_id=str(item["id"])
            chunkCount=item["chunkCount"]
            file_name=str(item["name"])
            if temp_id == fileId:
                logger.debug("Finished fetching file details.")
                break
    
    return [chunkCount, file_name]

#===============================================================================
# This function returns the user's Anaplan ID
#===============================================================================
def get_user_id(conn):
    '''
    @param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    '''
    
    url='https://api.anaplan.com/2/0/users/me'
    
    authorization = conn.authorization

    get_header = {
                "Authorization": authorization
                }
    
    logger.debug("Fetching user ID...")
    #print("Fetching user ID...")
    
    try:
        logger.debug("Retrieving details of current user.")
        user_details=requests.get(url, headers=get_header)
        user_details.raise_for_status()
    except Exception as e:
        logger.error("Error getting user details {0}".format(e))
    try:
        logger.debug("User details retrieved.")
        user_details=json.loads(user_details.text)
    except ValueError as e:
        logger.error("Error loading user details: {0}".format(e))
    
    try:
        user_id=user_details["user"]["id"]
    except ValueError as e:
        logger.error("Error loading user ID: {0}".format(e))
    
    return user_id

#===============================================================================
# This function queries Anaplan for a list of models the designated user has
# access to and returns this as a JSON array.
#===============================================================================
def get_models(conn, user_id):
    '''
    @param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    @param user_id: 32-character string that uniquely identifies the Anaplan user
    '''

    url = ''.join(["https://api.anaplan.com/2/0/users/", str(user_id), "/models"])

    authorization = conn.authorization

    get_header = {
                "Authorization": authorization , 
                "Content-Type":"application/json"
                }

    logger.debug("Fetching models")

    try:
        model_list=requests.get(url, headers=get_header)
    except ValueError as e:
        logger.error("Error getting models list: {0}".format(e))
    try:
        model_list=json.loads(model_list.text)
    except ValueError as e:
        logger.error("Error loading models list from JSON: {0}".format(e))

    try:
        model_list=model_list["models"]
    except ValueError as e:
        logger.error("Error loading models list: {0}".format(e))

    logger.debug("Finished fetching models.")
    
    return model_list

#===============================================================================
# This function returns the list of Anaplan workspaces a user may access as a
# JSON array
#===============================================================================
def get_workspaces(conn, user_id):
    '''
    @param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    @param user_id: 32-character string that uniquely identifies the Anaplan user
    '''

    url = ''.join(["https://api.anaplan.com/2/0/users/", str(user_id), "/workspaces"])

    authorization = conn.authorization

    get_header = {
                "Authorization": authorization ,
                "Content-Type":"application/json"
                }

    logger.debug("Fetching workspaces.")

    try:
        workspace_list=requests.get(url, headers=get_header)
    except ValueError as e:
        logger.error("Error getting workspace list: {0}".format(e))
    try:
        workspace_list=json.loads(workspace_list.text)
    except ValueError as e:
        logger.error("Error loading workspace list from JSON: {0}".format(e))

    try:
        model_list=workspace_list["workspaces"]
    except ValueError as e:
        logger.error("Error locating workspace list: {0}".format(e))

    logger.debug("Finished fetching workspaces.")

    return model_list
