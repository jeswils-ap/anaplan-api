import requests
import json
import os
import logging
import numpy as np

#===============================================================================
# Defining global variables
#===============================================================================
__base_url__ = "https://api.anaplan.com/2/0/workspaces"
__post_body__ = {
            "localeName":"en_US"
        }
__MB__ = 1024 * 1024
__chunk__ = 0

logger = logging.getLogger(__name__)

def upload(conn, fileId, chunkSize, file):
    '''
    :param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
    :param fileId: ID of the file in the Anaplan model
    :param chunkSize: Desired size of the chunk, in megabytes
    :param file: Path to the local file to be uploaded to Anaplan

    :return: None
    '''
    
    #Setting local variables for connection details
    authorization = conn.authorization
    workspaceGuid = conn.workspaceGuid
    modelGuid = conn.modelGuid
    
    #Enforce chunk size to fall between 1-50 mb
    if chunkSize < 1 or  chunkSize > 50:
        logger.error("CHunk size must be between 1-50.")
        chunkSize = np.clip(chunkSize, 1, 50)
        logger.info("Chunk size automatically set to {0}".format(chunkSize))

    #Assigning the size of the local file in MB
    file_size = os.stat(file).st_size / __MB__
    
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
                  "chunkCount": file_size / (__MB__ * chunkSize)
                 }
    url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/files/", fileId])

    metadata_update = file_metadata(url, post_header, file_metadata_start)
    #Confirm that the metadata update for the requested file was OK before proceeding with file upload
    if metadata_update:
        logger.info("Starting file upload.")

        complete = file_data(url, put_header, file, chunkSize)

        if complete:
            complete_upload = file_metadata(''.join([url, "/complete"]), post_header, file_metadata_complete)
            if complete_upload:
                logger.info("File upload complete, ")

def file_metadata(url, post_header, file_metadata):
    try:
        logger.debug("Updating file metadata.")
        meta_post = requests.post(url, headers=post_header, json=file_metadata)
        logger.debug("Complete!")
    except Exception as e:
        logger.error("Error setting metadata {0}".format(e))

    if meta_post.ok:
        return True

def file_data(url, put_header, file, chunkSize):
    file_data = []

    with open(file, "rt") as f: #Loop through the file, reading a user-defined number of bytes until complete
        chunkNum = 0
        while True:
            buf = f.readlines(__MB__ * chunkSize)
            if not buf:
                break
            for item in buf:
                file_data.append(item)
            try:
                logger.debug("Starting upload of chunk {0}".format(str(chunkNum + 1)))
                file_upload = requests.put(''.join([url, "/chunks/", str(chunkNum)]), headers=put_header, data=''.join(file_data).encode('utf-8'))
            except Exception as e:
                logger.error("Error uploading chunk {0}, {1}".format(chunkNum, e))
            logger.debug("Chunk {0} uploaded successfully.".format(str(chunkNum + 1)))

            if not file_upload.ok:
                complete = False #If the upload fails, break the loop and prevent subsequent requests. Print error to screen
                return False
            else:
                chunkNum += 1
    return True
