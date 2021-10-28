import requests
import json
import os
import logging
from io import StringIO

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

def upload(conn, file_id, chunkSize, data):
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
    stream_metadata = {
                        "id":file_id,
                        "chunkCount":-1
                          }
    url = __base_url__ + "/" +workspaceGuid + "/models/" + modelGuid + "/files/" + file_id

    ioData = StringIO(data)
    #Find length of data stream
    ioDataEnd = ioData.seek(0, os.SEEK_END)
    #Reset index back to 0 for reading
    ioData.seek(0)

        #Enforce chunk size to fall between 1-50 mb
    if chunkSize < 1 or  chunkSize > 50:
        logger.error("CHunk size must be between 1-50.")
        chunkSize = np.clip(chunkSize, 1, 50)
        logger.info("Chunk size automatically set to {0}".format(chunkSize))

    

    logger.info("Starting file upload...")
    start_upload_post = file_metadata(url, post_header, stream_metadata)

    while ioData.tell() != ioDataEnd:
        data = ioData.read(chunkSize * __MB__)
        stream_upload = file_data(''.join([url, "/chunks/", str(__chunk__)]), put_header, data.encode('utf-8'))
        __chunk__ += 1
        logger.debug("Successfully uploaded chunk number %s", str(__chunk__))

    complete_upload = file_metadata(''.join([url,"/complete"]), post_header, stream_metadata)
    if complete_upload:
        logger.info("File upload complete.")
        logger.debug("{0} chunk(s) successfully uploaded to Anaplan.".format(__chunk__))
        __chunk__ = 0

def file_metadata(url, post_header, stream_metadata):
    meta_post = None
    try:
        logger.debug("Updating file metadata.")
        meta_post = requests.post(url, headers=post_header, json=stream_metadata)
        logger.debug("Complete!")
    except Exception as e:
        logger.error("Error setting metadata {0}".format(e))

    if meta_post.ok:
        return True

def file_data(url, put_header, data):
    stream_upload = None
    try:
        logger.debug("Attempting to upload chunk {0}".format((str(__chunk__ + 1))))
        stream_upload = requests.put(url, headers=put_header, data=data)
        logger.debug("Chunk {0} uploaded successfully.".format(str(__chunk__ + 1)))
    except Exception as e:
        logger.error("Error uploading chunk {0}, {1}".format(__chunk__, e))

    if stream_upload.ok:
        return True