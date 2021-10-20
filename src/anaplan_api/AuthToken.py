#===============================================================================
# Created:        20 Oct 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Class to contain Anaplan Auth Token details required for all API calls
# Input:          Auth token value and expiry
# Output:         None
#===============================================================================

class AuthToken(object):
    '''
    classdocs
    '''

    def __init__(self, token_value, token_expiry):
        '''
        :param token_value: Auth token value
        :param token_expiry: Epoch time when token expires
        '''
        
        self.token_value = token_value
        self.token_expiry = token_expiry

    def get_auth_token():
        return self.authorization

    def set_auth_token(token_value):
        self.token_value = token_value

    def get_token_expiry():
        return self.token_expiry

    def set_token_expiry(token_expiry):
        self.token_expiry = token_expiry