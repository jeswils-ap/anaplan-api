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
from anaplan_api import anaplan_auth
from time import sleep
from requests.exceptions import HTTPError

#===============================================================================
# Defining global variables
#===============================================================================
__base_url__ = "https://api.anaplan.com/2/0/workspaces"
__post_body__ = {
            "localeName":"en_US"
        }
__BYTES__ = 1024 * 1024
__chunk__ = 0

logger = logging.getLogger

#===========================================================================
# This function sets the log level for the library.
#===========================================================================
def create_logger(level):
    '''
    :param level: Log level to report
    :param *args: If not null, path to file save logs.
    '''
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=level)
    logger = logging.getLogger("AnaplanPythonAPI")
    
    return logger
    

#===========================================================================
# This function reads the authentication type, Basic or Certificate, then passes
# the remaining variables to anaplan_auth to generate the authorization for Anaplan API
#===========================================================================
def generate_authorization(auth_type, *args):    
    '''
    :param auth_type: 
    :param *args: Path to public certificate, and private key if auth_type='certificate'; Anaplan Username, Anaplan 
                  Password, and private key if auth_type='basic'
    '''
    
    anaplan_auth.logger = logger
        
    if auth_type.lower() == 'basic':
        header_string = anaplan_auth.basic_auth_header(args[0], args[1])
        
        authorization = anaplan_auth.authenticate(anaplan_auth.auth_request(header_string, body=None))
        return authorization
    elif auth_type.lower() == 'certificate':
        privKey = args[0]
        pubCert = args[1]
        
        header_string = anaplan_auth.certificate_auth_header(pubCert)
        post_data = anaplan_auth.generate_post_data(privKey)
        
        authorization = anaplan_auth.authenticate(anaplan_auth.auth_request(header_string, post_data))
        if not authorization[:5] == "Error":
            return authorization   
        else:
            logger.error("Authentication Failed: %s", authorization)
            #print("Authentication Failed: " + authorization) 
    else:
        logger.error("Please enter a valid authentication method: Basic or Certificate")

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
    
    #Setting local variables for connection details
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    #Restrict users from entering a value for chunkSize greater than 50mb to prevent issues with API server
    if chunkSize > 50:
        logger.error("Chunk size must be 50mb or less.")
    else:
        
        #Assigning the size of the local file in MB
        file_size = os.stat(file).st_size / __BYTES__
        file_data = ""
        
        post_header = {
                "Authorization": authorization,
                "Content-Type":"application/json"
            }
        put_header = {
                "Authorization": authorization,
                "Content-Type":"application/octet-stream"
            }
        file_metadata_start = {
                    "id":fileId,
                    "chunkCount":-1
                      }
        file_metadata_complete = {
                      "id":fileId,
                      "chunkCount": file_size / (__BYTES__ * chunkSize)
                     }
        url = __base_url__ + "/" +workspaceGuid + "/models/" + modelGuid + "/files/" + fileId
    
        try:
            logger.debug("Resetting file metadata.")
            start_upload_post = requests.post(url, headers=post_header, json=file_metadata_start)
            start_upload_post.raise_for_status()
            logger.debug("Complete!")
        except HTTPError as e:
            raise HTTPError(e)
        #Confirm that the metadata update for the requested file was OK before proceeding with file upload
        if start_upload_post.ok:
            logger.info("Starting file upload.")
            complete = True #Variable to track whether file has finished uploaded
            with open(file, "rt") as f: #Loop through the file, reading a user-defined number of bytes until complete
                chunkNum = 0
                while True:
                    buf=f.readlines(__BYTES__ * chunkSize)
                    if not buf:
                        break
                    for item in buf:
                        file_data += item
                    try:
                        logger.debug("Starting upload of chunk %s", str(chunkNum + 1))
                        file_upload = requests.put(url + "/chunks/" + str(chunkNum), headers=put_header, data=file_data.encode('utf-8'))
                        file_upload.raise_for_status()
                    except HTTPError as e:
                        raise HTTPError(e)
                    logger.debug("Chunk %s uploaded successfully.", str(chunkNum + 1))
                    #print("Chunk " + str(chunkNum + 1) +" uploaded, Status: " + str(file_upload.status_code))
                    if not file_upload.ok:
                        complete = False #If the upload fails, break the loop and prevent subsequent requests. Print error to screen
                        logger.error("Error %s\n%s", str(file_upload.status_code), file_upload.text)
                        break
                    else:
                        chunkNum += 1    
            if complete:
                complete_upload = requests.post(url + "/complete", headers=post_header, json=file_metadata_complete)
                if complete_upload.ok:
                    logger.info("File upload complete, ")
                    logger.debug("%s chunk(s) uploaded to the server.", str(chunkNum))
                else:
                    logger.error("There was an error with your request: %s %s", complete_upload.status_code, complete_upload.text)
        else:
            logger.error("There was an error with your request: %s %s", start_upload_post.status_code, start_upload_post.text)

#===========================================================================
# This function uploads a data stream to Anaplan in a chunk of no larger
# than 50mb. 
#===========================================================================
def stream_upload(conn, file_id, buffer, **args):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param fileId: ID of the file in the Anaplan model
    :param buffer: data to uplaod to Anaplan file
    :param *args: Once complete, this should be True to complete upload and reset chunk counter
    '''
    
    global __chunk__
    
    #Setting local variables for connection details
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    post_header = {
                    "Authorization": authorization,
                      "Content-Type":"application/json"
                }
    put_header = {
                    "Authorization": authorization,
                    "Content-Type":"application/octet-stream"
                }
    stream_metadata_start = {
                        "id":file_id,
                        "chunkCount":-1
                          }
    url = __base_url__ + "/" +workspaceGuid + "/models/" + modelGuid + "/files/" + file_id
    
    if(len(args) > 0):  
        file_metadata_complete = {
                      "id":file_id,
                      "chunkCount": -1
                     }
        try:
            complete_upload = requests.post(url=url + "/complete", headers=post_header, json=file_metadata_complete)
            complete_upload.raise_for_status()
        except HTTPError() as e:
            raise HTTPError(e)
        if complete_upload.ok:
            logger.info("File upload complete.")
            logger.debug("%s chunk(s) successfully uploaded to Anaplan.", __chunk__)
        else:
            logger.error("There was an error completing your upload: %s \n %s", complete_upload.status_code, complete_upload.text)
            #return "There was an error completing your upload: " + complete_upload.status_code + '\n' + complete_upload.text     
        __chunk__ = 0
    else:
        if(len(buffer.encode()) > (__BYTES__ * 50)):
            logger.error("Buffer too large, please send less than 50mb of data.")
            #return "Buffer too large, please send less than 50mb of data."
        else:
            if __chunk__ == 0:    
                logger.info("Starting file upload...")    
                try:
                    start_upload_post = requests.post(url, headers=post_header, json=stream_metadata_start)
                    start_upload_post.raise_for_status()
                except HTTPError() as e:
                    raise HTTPError(e)
            #Confirm that the metadata update for the requested file was OK before proceeding with file upload
            try:
                logger.debug("Attempting to upload chunk %s...", (str(__chunk__ + 1)))
                stream_upload = requests.put(url + "/chunks/" + str(__chunk__), headers=put_header, data=buffer.encode('utf-8'))
                stream_upload.raise_for_status()
            except HTTPError() as e:
                raise HTTPError(e)
            if not stream_upload.ok:
                logger.error("Error %s\n%s", str(stream_upload.status_code), stream_upload.text)
                #return "Error " + str(stream_upload.status_code) + '\n' + stream_upload.text
            else:
                __chunk__ += 1
                logger.debug("Successfully uploaded chunk number %s", str(__chunk__))
                #return "Uploaded chunk " + str(__chunk__) + ", Status: " + str(stream_upload.status_code)
            

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
        url = __base_url__ + "/" +workspaceGuid + "/models/" + modelGuid + "/imports/" + actionId + "/tasks"
        logger.info("Running action %s", actionId)
        if actionId[:3] == "112":
            taskId = run_action(url, post_header, retryCount)
            return check_status(url, taskId, post_header)
        elif actionId[:3] == "116":
            taskId = run_action(url, post_header, retryCount)
            return check_status(url, taskId, post_header)
        elif actionId[:3] == "117":
            taskId = run_action(url, post_header, retryCount)
            return check_status(url, taskId, post_header)
        elif actionId[:3] == "118":
            taskId = run_action(url, post_header, retryCount)
            return check_status(url, taskId, post_header)
    else:
        logger.error("Incorrect action ID provided!")

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
            run_action.raise_for_status()
        except HTTPError() as e:
            raise HTTPError(e)
        if run_action.status_code != 200 and state < retryCount:
            sleep(sleepTime)
            try:
                run_action = requests.post(url, headers=post_header, json=__post_body__)
                run_action.raise_for_status()
            except HTTPError() as e:
                raise HTTPError(e)
            state += 1
            sleepTime = sleepTime * 1.5
        else:
            break
    taskId = json.loads(run_action.text)
    taskId = taskId["task"]
    
    return taskId["taskId"]
        
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
    
    if len(params) > 1:
        for key, value in params.items():
            body += "\"entityType:\"" + key + "\"" + ",\"entityType:\"" + value + "\"" + ","
        body = body[:-1]
        body = "[" + body + "]"
    else:
        for key, value in params.items():
            body += "[\"" + key + "\"" + ":" + "\"" + value + "\"]"
    
    
    post_body = {
                    "localeName":"en_US","mappingParameters": body
                }
    
    if actionId[2] == "2" or actionId[2] == "8":
        logger.info("Running action %s", actionId)
        url = __base_url__ + "/" +workspaceGuid + "/models/" + modelGuid + "/imports/" + actionId + "/tasks"
        if actionId[:3] == "112":
            taskId = run_action_with_parameters(url, post_header, retryCount, post_body)
            return check_status(url, taskId, post_header)
        elif actionId[:3] == "118":
            taskId = run_action(url, post_header, retryCount, post_body)
            return check_status(url, taskId, post_header)
    else:
        logger.error("Incorrect action ID provided! Only imports and processes may be executed with parameters.")

#===========================================================================
# This function executes the Anaplan import or process with mapping parameters,
# if there is a server error it will wait, and retry a number of times
# defined by the user. Once the task is successfully created, the task ID is returned.
#===========================================================================
def run_action_with_parameters(url, post_header, retryCount, post_body):
    '''
    @param url: POST URL for Anaplan action
    @param post_header: Authorization header string
    @param retryCount: Number of times to retry executino of the action
    '''
    
    state = 0
    sleepTime = 10
        
    while True:
        try:
            run_action = requests.post(url, headers=post_header, json=post_body)
            run_action.raise_for_status()
        except HTTPError as e:
            raise HTTPError(e)
        if run_action.status_code != 200 and state < retryCount:
            sleep(sleepTime)
            try:
                run_import = requests.post(url, headers=post_header, json=post_body)
                run_import.raise_for_status()
            except HTTPError as e:
                raise HTTPError(e)
            state += 1
            sleepTime = sleepTime * 1.5
        else:
            break
    taskId = json.loads(run_import.text)
    
    return taskId["taskId"]

#===========================================================================
# This function monitors the status of Anaplan action. Once complete it returns
# the JSON text of the response.
#===========================================================================        
def check_status(url, taskId, post_header):
    '''
    @param url: Anaplan task URL
    @param taskId: ID of the Anaplan task executed
    @param post_header: Authorization header value
    '''
    
    while True:
        try:
            get_status = requests.get(url + "/" + taskId, headers=post_header)
            get_status.raise_for_status()
        except HTTPError as e:
            raise HTTPError(e)
        status = json.loads(get_status.text)
        status = status["task"]["taskState"]
        if status == "COMPLETE":
            results = json.loads(get_status.text)
            results = results["task"]
            break   
    
    return parse_task_response(results, url, taskId, post_header)
    
#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
def parse_task_response(results, url, taskId, post_header):
    '''
    :param results: JSON dump of the results of an Anaplan action
    '''
    
    job_status = results["currentStep"]
    failure_alert = str(results["result"]["failureDumpAvailable"])
    
    if job_status == "Failed.":
        error_message = str(results["result"]["details"][0]["localMessageText"])
        logger.error("The task has failed to run due to an error: %s", error_message)
        #print("The task has failed to run due to an error: " + error_message)
        #return "The task has failed to run due to an error: " + error_message
    else:
        if failure_alert == "True":
            try:
                dump = requests.get(url + "/" + taskId + '/' + "dump", headers=post_header)
                dump.raise_for_status()
            except HTTPError as e:
                raise HTTPError(e)
            dump = dump.text
        success_report = str(results["result"]["successful"])
        if 'details' not in results["result"]:
            anaplan_process_dump = ""
            error_detail = ""
            load_detail = ""
            failure_details = ""
            for nestedResults in results["result"]["nestedResults"]:
                process_subfailure = str(nestedResults["failureDumpAvailable"])
                object_id = str(nestedResults["objectId"])
                load_detail = load_detail + "Process action " + object_id + " completed. Failure: " + process_subfailure + '\n'
                if process_subfailure == "True":
                        local_message = str(nestedResults["details"][0]["localMessageText"])
                        details = nestedResults["details"][0]["values"]
                        for i in details:
                            error_detail = error_detail + i + '\n'
                        try:
                            dump = requests.get(url + "/" + taskId + '/' + "dumps" + '/' + object_id,  headers=post_header)
                            dump.raise_for_status()
                        except HTTPError as e:
                            raise HTTPError(e)
                        report = "Error dump for " + object_id + '\n' + dump.text
                        anaplan_process_dump += report  
                        failure_details = failure_details + local_message      
            if anaplan_process_dump != "":
                logger.info("The requested job is %s", job_status)
                #print("The requested job is " + job_status)
                logger.info("%s\nDeails:\n%s\nFailure dump(s):\n%s", load_detail, error_detail, anaplan_process_dump)
                #return load_detail + '\n' + "Details:" + '\n' + error_detail + '\n' + "Failure dump(s):" + '\n' + anaplan_process_dump
            else:
                logger.info("The requested job is %s", job_status)
                #print("The requested job is " + job_status)
                logger.info(load_detail)
                #return load_detail
        else:
            if "details" in results["result"]:
                if str(results["result"]["details"][0]["type"]) == "exportSucceeded":
                    size = results["result"]["details"][0]["values"][1]
                    name = results["result"]["details"][0]["values"][5]
                    return "Export complete! Files size: " + str(size) + " bytes. File name: " + str(name)
                else:
                    load = str(results["result"]["details"][0]["localMessageText"])
                    load_detail = ""
                    for i in results["result"]["details"][0]["values"]:
                        load_detail = load_detail + i + '\n'
                    if failure_alert == "True":
                        logger.info("The requested job is %s", job_status)
                        #print("The requested job is " + job_status)
                        logger.error("Failure Dump Available: %s, Successful: %s\nLoad details:\n%s\n%s\nFailure dump:\n%s", failure_alert, success_report, load, load_detail, dump)
                        #return "Failure Dump Available: " + failure_alert + ", Successful: " + success_report + '\n' + "Load details:" + '\n' + load + '\n' + load_detail + '\n' + "Failure dump:" + '\n' + dump
                    else:
                        logger.info("The requested job is %s", job_status)
                        #print("The requested job is " + job_status)
                        logger.error("Failure Dump Available: %s, Successful: %s\nLoad details:\n%s\n%s", failure_alert, success_report, load, load_detail)
                        #return "Failure Dump Available: " + failure_alert + ", Successful: " + success_report + '\n' + "Load details:" + '\n' + load + '\n' + load_detail
                

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
    url = __base_url__ + "/" + workspaceGuid + "/models/" + modelGuid + "/" + resource.lower()
    
    logger.debug("Fetching %s", resource)
    #print("Fetching " + resource + "...")
    
    try:
        response = requests.get(url, headers=get_header)
        response.raise_for_status()
    except HTTPError as e:
        raise HTTPError(e)
    response = response.text
    response = json.loads(response)
    
    logger.debug("Finished fetching %s", resource)
    #print("Finished fetching " + resource + ".")
     
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
            logger.info("Name: %s\nID: %s\n", item["name"], item["id"])
            #print("Name: " + item["name"] + '\n' + "ID: " + item["id"] + '\n')
            
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
    
    url = __base_url__ + "/" + workspaceGuid + "/models/" + modelGuid + "/files/" + fileId + "/chunks/"
    
    logger.info("Starting download of file %s", fileId)
    
    file = ""
    
    while int(chunk) < int(chunk_count):
        try:
            logger.debug("Downloading chunk %s", chunk)
            file_contents = requests.get(url + str(chunk), headers=get_header)
            file_contents.raise_for_status()
        except HTTPError as e:
            raise HTTPError(e)
        if file_contents.ok:
            logger.debug("Chunk %s downloaded successfully.", chunk)
            file += file_contents.text
        else:
            logger.error("There was a problem downloading %s", file_name)
            #return "There was a problem fetching the file: " + file_name
            break
        chunk = str(int(chunk) + 1)
        
    if int(chunk) == int(chunk_count):
        logger.info("File download complete!")
        #print("File download complete!")
        
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
    
    url = __base_url__ + "/" + workspaceGuid + "/models/" + modelGuid + "/files/"
    
    try:
        files_list = requests.get(url, headers=get_header)
        files_list.raise_for_status()
    except HTTPError as e:
        raise HTTPError(e)
    
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
    except HTTPError as e:
        raise HTTPError(e)
    try:
        logger.debug("User details retrieved.")
        user_details=json.loads(user_details.text)
    except ValueError as e:
        logger.error("Error loading user details: %s", e)
    
    try:
        user_id=user_details["user"]["id"]
    except ValueError as e:
        logger.error("Error loading user ID: %s", e)
    
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
    
    url="https://api.anaplan.com/2/0/users/" + str(user_id) + "/models"
    
    authorization = conn.authorization

    get_header = {
                "Authorization": authorization , 
                "Content-Type":"application/json"
                }
    
    logger.debug("Fetching models")
    #print("Fetching models...")
    
    try:
        model_list=requests.get(url, headers=get_header)
    except ValueError as e:
        logger.error("Error getting models list: %s", e)
    try:
        model_list=json.loads(model_list.text)
    except ValueError as e:
        logger.error("Error loading models list from JSON: %s", e)
    
    try:
        model_list=model_list["models"]
    except ValueError as e:
        logger.error("Error loading models list: %s", e)
    
    logger.debug("Finished fetching models.")
    #print("Finished fetching models.")
    
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
    
    url="https://api.anaplan.com/2/0/users/" + str(user_id) + "/workspaces"
    
    authorization = conn.authorization

    get_header = {
                "Authorization": authorization ,
                "Content-Type":"application/json"
                }
    
    logger.debug("Fetching workspaces.")
    #print("Fetching workspaces...")
    
    try:
        workspace_list=requests.get(url, headers=get_header)
    except ValueError as e:
        logger.error("Error getting workspace list: %s", e)
    try:
        workspace_list=json.loads(workspace_list.text)
    except ValueError as e:
        logger.error("Error loading workspace list from JSON: %s", e)
    
    try:
        model_list=workspace_list["workspaces"]
    except ValueError as e:
        logger.error("Error locating workspace list: %s", e)
    
    logger.debug("Finished fetching workspaces.")
    #print("Finished fetching workspaces.")
    
    return model_list
