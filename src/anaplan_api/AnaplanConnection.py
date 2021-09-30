#===============================================================================
# Created:        13 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Class to contain Anaplan connection details required for all API calls
# Input:          Authorization header string, workspace ID string, and model ID string
# Output:         None
#===============================================================================

class AnaplanConnection(object):
    '''
    classdocs
    '''


    def __init__(self, authorization, workspaceGuid, modelGuid):
        '''
        :param authorization: Authorization header string
        :param workspaceGuid: ID of the Anaplan workspace
        :param modelGuid:     ID of the Anaplan model
        '''
        
        self.authorization = authorization
        self.workspaceGuid = workspaceGuid
        self.modelGuid = modelGuid
        