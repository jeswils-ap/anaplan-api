# anaplan-api

Anaplan-API is a Python library wrapper for [Anaplan Bulk API](https://anaplanbulkapi20.docs.apiary.io/) and [Anaplan Authentication API](https://anaplanauthentication.docs.apiary.io/).

## Installation

Use the package manager [pip](https://pypi.org/project/anaplan-api/) to install Anaplan-API.

```bash
pip install anaplan_api
```

## Usage

```python
from anaplan_api import anaplan
from anaplan_api.AnaplanConnection import AnaplanConnection
from anaplan_api.KeystoreManager import KeystoreManager

# Generate Basic Auth token for API requests
keys = KeystoreManager(path='/keystore.jks', passphrase='', alias='', key_pass='')

auth = anaplan.generate_authorization('Certificate', private_key=keys.get_key(), cert=keys.get_cert())

# Create connection object to interact with API
# For now, the package expected the first object of AnaplanConnect to contain only the auth token
# not the AuthToken object
conn = AnaplanConnection(auth.get_auth_token(), "workspaceId", "modelId")

# Pass path to the file to be uploaded.
anaplan.file_upload(conn=conn, file_id="", chunk_size=5, data='/file.csv')

# Read filee into memory and pass to file_upload
with open('/file.csv', 'r') as file:
	data = file.read()
	ap.file_upload(conn=conn, file_id="", chunk_size=5, data=data)

# Execute Anaplan action
# Returns a strint with task results and error dumps if any
result_arr = anaplan.execute_action(conn=conn, action_id="", retry_count=3)

# Loop through List[ParserResponse] and print contents of each ParserResonse object.
# ParserResponse contains overall task details, option export file (if an export action or process with export was executed)
# whether an error dump was generated, and and option dataframe with error dump if available.
for item in result_arr:
	print(item)
```

## Requirements
This library currently uses PyJKS library for handling Java Keystore files. This project does not appear to be actively developed, and there is a known error installing pycryptodomex and twofish - both dependencies for PyJKS. The core files required from this library are:

- jks.py
- rfc2898.py
- sun_crypto.py
- util.py

You can simply download, remove extraneous files, and drop the jks folder in your site-package directory to work around the error.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[BSD](https://opensource.org/licenses/BSD-2-Clause)