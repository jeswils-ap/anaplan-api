#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
import requests, json
import pandas as pd
import logging
from io import StringIO

logger = logging.getLogger(__name__)

def parse_response(results, url, taskId, post_header):
    '''
    :param results: JSON dump of the results of an Anaplan action
    :returns: String with task details, data load details string, and an array of error dump dataframes
    '''
    #Create placeholder objects
    eDf = pd.DataFrame()
    msg = []

    logger.debug("Parsing import details")

    job_status = results["currentStep"]
    failure_dump = str(results["result"]["failureDumpAvailable"])

    if job_status == "Failed.":
        error_message = str(results["result"]["details"][0]["localMessageText"])
        logger.error("The task has failed to run due to an error: {0}".format(error_message))
        return ("The task has failed to run due to an error: {0}".format(error_message), error_dumps)
    else:
        #IF failure dump is available download
        if str(failure_dump) == "True":
            try:
                logger.debug("Fetching error dump.")
                dump = requests.get(url + "/" + taskId + '/' + "dump", headers=post_header).text
                eDf = pd.read_csv(StringIO(dump))
                logger.debug("Failure dump downloaded.")
            except Exception as e:
                logger.error("Error downloading error dump {0}".format(e))

        success_report = str(results["result"]["successful"])

        #details key only present in import task results
        if 'details' in results["result"]:
            logger.info("Fetching import details.")
            for i in range(0, len(results["result"]["details"])):
                if 'localMessageText' in results["result"]["details"][i]:
                    msg.append(str(results["result"]["details"][i]["localMessageText"]))
                    if 'values' in results["result"]["details"][i]:
                        for detail in results["result"]["details"][i]["values"]:
                            msg.append(detail)

        logger.info("The requested job is %s", job_status)
        logger.info("Failure Dump Available: {0}, Successful: {1}".format(failure_dump, success_report))
        return ["Failure Dump Available: {0}, Successful: {1}".format(failure_dump, success_report), '\n'.join(msg), eDf]