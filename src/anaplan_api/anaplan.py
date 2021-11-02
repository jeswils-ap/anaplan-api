#===============================================================================
# Created:        11 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    This library implements the Anaplan API to get lists of model resources, upload files to Anaplan server, 
#                 download files from Anaplan server, and execute actions.
#===============================================================================

import requests, json, logging
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from anaplan_api.ImportParser import ImportParser
from anaplan_api.ExportParser import ExportParser
from anaplan_api.ActionParser import ActionParser
from anaplan_api.ProcessParser import ProcessParser
from anaplan_api.BasicAuthentication import BasicAuthentication
from anaplan_api.CertificateAuthentication import CertificateAuthentication
from anaplan_api.FileUpload import FileUpload
from anaplan_api.StreamUpload import StreamUpload
from anaplan_api.Action import Action

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
		basic = BasicAuthentication()
		header_string = basic.auth_header(args[0], args[1])
		authorization = basic.authenticate(basic.auth_request(header_string))
		return authorization
	elif auth_type.lower() == 'certificate':
		cert = CertificateAuthentication()
		privKey = args[0]
		pubCert = args[1]
		
		header_string = cert.auth_header(pubCert)
		post_data = cert.generate_post_data(privKey)
		authorization = cert.authenticate(cert.auth_request(header_string, post_data))
	else:
		logger.error("Please enter a valid authentication method: Basic or Certificate")
		return None

	if authorization[0]:
		auth_token = authorization[0]
		if not auth_token[:5] == "Error":
			return authorization   
		else:
			logger.error(f"Authentication Failed: {auth_token}")
	

#===========================================================================
# This function reads a flat file of an arbitrary size and uploads to Anaplan
# in chunks of a size defined by the user.
#===========================================================================
def flat_file_upload(conn, file_id, chunk_size, file):
	'''
	:param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
	:param fileId: ID of the file in the Anaplan model
	:param chunkSize: Desired size of the chunk, in megabytes
	:param file: Path to the local file to be uploaded to Anaplan
	'''
	flat = FileUpload(conn, file_id)
	flat.upload(chunk_size, file)

#===========================================================================
# This function uploads a data stream to Anaplan in a chunk of no larger
# than 50mb. 
#===========================================================================
def stream_upload(conn, file_id, chunk_size, data):
	'''
	:param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
	:param fileId: ID of the file in the Anaplan model
	:param buffer: data to uplaod to Anaplan file
	:param *args: Once complete, this should be True to complete upload and reset chunk counter
	'''

	stream = StreamUpload(conn, file_id)
	stream.upload(chunk_size, data)

#===========================================================================
# This function reads the ID of the desired action to run, POSTs the task
# to the Anaplan API to execute the action, then monitors the status until
# complete.
#===========================================================================
def execute_action(conn, action_id, retry_count, *args):
	'''
	:param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
	:param actionId: ID of the action in the Anaplan model
	:param retryCount: The number of times to attempt to retry the action if it fails
	'''
	
	if len(args) == 0:
		task = Action(conn, action_id, retry_count)
		task_details = task.execute()
		#Missing url, task ID, and post_header -> Double check how these are used
		return parse_task_response(conn, task_details[0], task_details[1], action_id)
	else:
		task = ParameterAction(conn, action_id, retry_count, args)
		task_details = task.execute()
		return parse_task_response(conn, task_details[0], task_details[1], action_id)


#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
def parse_task_response(conn, results, url, action_id):
	'''
	:param results: JSON dump of the results of an Anaplan action
	:returns: String with task details, array of error dump dataframes
	'''
	
	if action_id[:3] == "112":
		#Import
		return ImportParser(results, url)
	elif action_id[:3] == "116":
		#Export
		return ExportParser(conn, results, url)
	elif action_id[:3] == "117":
		#Action
		return ActionParser(results, url)
		return
	elif action_id[:3] == "118":
		#Process
		return ProcessParser(conn, results, url)

#===========================================================================
# This function queries the Anaplan model for a list of the desired resources:
# files, actions, imports, exports, processes and returns the JSON response.
#===========================================================================
def get_list(conn, resource):
	'''
	:param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
	:param resource: The Anaplan model resource to be queried and returned to the user
	'''

	authorization = conn.get_auth()
	workspaceGuid = conn.get_workspace()
	modelGuid = conn.get_model()

	get_header = {
			'Authorization': authorization,
			'Content-Type':'application/json'
	}

	url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/", resource.lower()])

	logger.debug(f"Fetching {resource}")
	try:
		response = json.loads(requests.get(url, headers=get_header, timeout=(5,30)).text)
	except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
		logger.error(f"Error fetching resource {resource}, {e}")
	logger.debug(f"Finished fetching {resource}")

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
			logger.info(f"Name: {item['name']}\nID: {item['id']}\n")
			
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

	authorization = conn.get_auth()
	workspaceGuid = conn.get_workspace()
	modelGuid = conn.get_model()

	get_header = {
				"Authorization": authorization,
	}    

	url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/files/", fileId, "/chunks/"])

	logger.info(f"Starting download of file {fileId}")

	file = ""

	while int(chunk) < int(chunk_count):
		try:
			logger.debug(f"Downloading chunk {chunk}")
			file_contents = requests.get(''.join([url, str(chunk)]), headers=get_header, timeout=(5,30))
			file_contents.raise_for_status()
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error downloading chunk {e}")
		if file_contents.ok:
			logger.debug(f"Chunk {chunk} downloaded successfully.")
			file += file_contents.text
		else:
			logger.error(f"There was a problem downloading {file_name}")
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

	authorization = conn.get_auth()
	workspaceGuid = conn.get_workspace()
	modelGuid = conn.get_model()

	get_header = {
				"Authorization": authorization,
	}

	url = ''.join([__base_url__, "/", workspaceGuid, "/models/", modelGuid, "/files/"])

	try:
		files_list = requests.get(url, headers=get_header, timeout=(5,30))
	except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
		logger.error(f"Error getting details for {fileId}, {e}")

	if files_list.ok:
		logger.debug("Fetching file details.")
		files=json.loads(files_list.text)
		files=files['files']
		for item in files:
			temp_id=str(item['id'])
			chunkCount=item['chunkCount']
			file_name=str(item['name'])
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

	authorization = conn.get_auth()

	get_header = {
				"Authorization": authorization
				}

	logger.debug("Fetching user ID...")

	try:
		logger.debug("Retrieving details of current user.")
		user_details = json.loads(requests.get(url, headers=get_header, timeout=(5,30)).text)
	except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
		logger.error(f"Error fetching user details {e}")
	except ValueError as e:
		logger.error(f"Error loading user details {e}")
	if 'user' in user_details:
		if 'id' in user_details['user']:
			user_id = user_details['user']['id']

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

	authorization = conn.get_auth()

	get_header = {
				"Authorization": authorization , 
				"Content-Type":"application/json"
				}

	logger.debug("Fetching models")

	try:
		model_list = json.loads(requests.get(url, headers=get_header, timeout=(5,30)).text)
	except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
		logger.error(f"Error getting models list: {e}")
	except ValueError as e:
		logger.error(f"Error loading model list {e}")

	if 'models' in model_list:
		models = model_list['models']
	logger.debug("Finished fetching models.")

	return models

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

	authorization = conn.get_auth()

	get_header = {
				"Authorization": authorization ,
				"Content-Type":"application/json"
				}

	logger.debug("Fetching workspaces.")

	try:
		workspace_list = json.loads(requests.get(url, headers=get_header, timeout=(5,30)).text)
	except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
		logger.error(f"Error getting workspace list: {e}")
	except ValueError as e:
		logger.error(f"Error loading workspace list {e}")

	if 'workspaces' in workspace_list:
		workspaces = workspace_list['workspaces']
	logger.debug("Finished fetching workspaces.")

	return workspaces
