#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
import anaplan
import requests, json
import pandas as pd
import logging
from io import StringIO

logger = logging.getLogger(__name__)

def parse_response(results, url, taskId, post_header):
    '''
    :param results: JSON dump of the results of an Anaplan action
    :returns: String with task details, action details as String, and an array of error dump dataframes
    '''
    
    job_status = results["currentStep"]
    failure_alert = str(results["result"]["failureDumpAvailable"])
    error_dumps = []
    
    if job_status == "Failed.":
        error_message = str(results["result"]["details"][0]["localMessageText"])
        logger.error("The task has failed to run due to an error: {0}".format(error_message))
        return ("The task has failed to run due to an error: {0}".format(error_message), None, error_dumps)
    else:
        #IF failure dump is available download
        if failure_alert == "True":
            try:
                dump = requests.get(url + "/" + taskId + '/' + "dump", headers=post_header).text
                dump.raise_for_status()
            except HTTPError as e:
                raise HTTPError(e)
            eDf = pd.read_csv(StringIO(dump))
            error_dumps.append(eDf)
        
        success_report = str(results["result"]["successful"])
        
        #details key only present in import task results
        if 'objectId' in results['result']:
            object_id = results['result']['objectId']
            action_detail = "{0} completed successfully: {1}".format(object_id, success_report)

            logger.info("The requested job is %s", job_status)
            logger.error("Failure Dump Available: {0}, Successful: {1}".format(failure_alert, success_report))
            return ["Failure Dump Available: {0}, Successful: {1}".format(failure_alert, success_report), action_detail, error_dumps]