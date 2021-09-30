#===============================================================================
# Created:        12 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    This library takes a JSON response and builds a key-value dictionary for easy traversal.
# Input:          A JSON text string
# Output:         Key-value dictionary object, resource name, or resource ID
#===============================================================================

import json

#===========================================================================
# This function builds a Python key-value diction with the ID as the key and
# returns it.
#===========================================================================
def build_id_dict(response, resource_type):
    '''
    :param response: JSON text response from Anaplan resource request
    :param resource_type: The Anaplan resource being polled in the GET request
    '''
    
    response_list = response
    resource_dict = {}
    
    for item in response_list:
        resource_dict[str(item["name"])] = str(item["id"])
    
    return resource_dict

#===========================================================================
# This function reads the ID-based key-value dictionary and returns the name 
# of the the Anaplan resource.
#===========================================================================
def get_id(resource_dict, resource_name):
    '''
    :param resource_dict: Key-value diction where resource name is the key
    :param resource_name: Resource name provided by user to be looked up
    '''
    
    return resource_dict.get(resource_name)

#===========================================================================
# This function builds a Python key-value diction with the name as the key and
# returns it.
#===========================================================================
def build_name_dict(response, resource_type):
    '''
    :param response: JSON text response from Anaplan resource request
    :param resource_type: The Anaplan resource being polled in the GET request
    '''
    
    response_list = json.loads(response)
    response_list = response_list[resource_type]
    resource_dict = {}
    
    for item in response_list:
        resource_dict[str(item["id"])] = str(item["name"])
        
    return resource_dict

#===========================================================================
# This function reads the ID-based key-value dictionary and returns the id 
# of the the Anaplan resource.
#===========================================================================
def get_name(resource_dict, resource_id):
    '''
    :param resource_dict: Key-value diction where resource id is the key
    :param resource_name: Resource id provided by user to be looked up
    '''
    
    return resource_dict.get(resource_id)