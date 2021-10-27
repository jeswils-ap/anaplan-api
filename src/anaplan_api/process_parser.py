#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
import requests, json
import pandas as pd
import logging, re
import anaplan
from io import StringIO

logger = logging.getLogger(__name__)

def parse_response(conn, results, url, taskId, post_header):
    '''
    :param conn: AnaplanConnection object
    :param results: JSON dump of the results of an Anaplan action
    :param: url Base url for task
    :param: taskId: 32-characher ID for task
    :param: post_header: Header string with authentication
    :returns: Array with String of overall task result, and array of process action details)
    '''
    
    job_status = results["currentStep"]
    failure_alert = str(results["result"]["failureDumpAvailable"])

    if job_status == "Failed.":
        logger.error("The task has failed to run due to an error, please check process definition in Anaplan")
        return ("The task has failed to run due to an error, please check process definition in Anaplan", None)
    else:
        logger.info("Process completed.")
        #nestedResults key only present in process task results
        if 'nestedResults' in results["result"]:
            nested_details = []
            
            logger.debug("Parsing nested results.")
            for nestedResults in results["result"]["nestedResults"]:
                #Array to store sub-process import details
                subprocess_detail = []

                subprocess_failure = str(nestedResults["failureDumpAvailable"])
                object_id = str(nestedResults["objectId"])
                subprocess_msg = "Process action {0} completed. Failure: {1}".format(object_id, subprocess_failure)

                logger.info("Fetching details for object {0}".format(object_id))
                objectDetails = sub_process_parser(conn, object_id, nestedResults, url, taskId, post_header)
                nested_details.append([objectDetails[0], objectDetails[1], objectDetails[2]])

            return nested_details

def sub_process_parser(conn, object_id, results, url, taskId, post_header):
    #Create placeholders objects
    eDf = pd.DataFrame()
    msg = []

    #Regex pattern for hierarchy parsing
    hReg = re.compile('hierarchyRows.+')

    failure_dump = results['failureDumpAvailable']
    successful = results['successful']

    print(failure_dump)
    if str(failure_dump) == "True":
        try:
            logger.info("Fetching error dump")
            dump = requests.get(url + "/" + taskId + '/' + "dumps" + '/' + object_id,  headers=post_header).text
            eDf = pd.read_csv(StringIO(dump))
        except Exception as e:
            logger.error("Error downloading error dump {0}".format(e))

    #Import specific parsing
    if 'details' in results:
        for i in range(0, len(results['details'])):
            #Import specific parsing
            if 'localMessageText' in results['details'][i]:
                msg.append(results['details'][i]['localMessageText'])
                #Parsing module imports with failures
                if 'values' in results['details'][i]:
                    for j in range(0, len(results['details'][i]['values'])):
                        msg.append(results['details'][i]['values'][j])
            if 'type' in results['details'][i]:
                #Parsing hierarchy import nested details
                if bool(re.match(hReg, results['details'][i]['type'])):
                    if 'values' in results['details'][i]:
                        for j in range(0, len(results['details'][i]['values'])):
                            msg.append(results['details'][i]['values'][j])
            #Export specific parsing
            if 'type' in results['details'][i]:
                if results['details'][i]['type'] == "exportSucceeded":
                    msg = anaplan.get_file(conn, object_id)


    logger.debug("Error dump available: {0}, Sub-task {1} successful: {2}".format(failure_dump, object_id, successful))
    return ["Error dump available: {0}, Sub-task {1} successful: {2}".format(failure_dump, object_id, successful), '\n'.join(msg), eDf]