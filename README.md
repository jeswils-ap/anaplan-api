# anaplan-api

Anaplan-API is a Python library wrapper for [Anaplan Bulk API](https://anaplanbulkapi20.docs.apiary.io/) and [Anaplan Authentication API](https://anaplanauthentication.docs.apiary.io/).

## Installation

Use the package manager [pip](https://pypi.org/project/anaplan-api/) to install Anaplan-API.

```bash
pip install anaplan-api
```

## Usage

```python
import anaplan-api as ap
from anaplan-api.AuthToken import AuthToken
from anaplan-api import keystore_manager as km
from anaplan-api.AnaplanConnection import AnaplanConnection

#Generate Basic Auth token for API requests
auth = ap.generate_authorization('Basic', 'user', 'password')

#Generate Cert Auth token for API requests
key_pair = km.get_keystore_pair('/path/to/keystore.jks', 'keystore_pass', 'key_alias', 'private_key_passphrase')
privKey = key_pair[0]
pubCert = key_pair[1]
authReq = ap.generate_authorization('Certificate', privKey, pubCert)
auth = AuthToken(authReq[0], authReq[1])

# Create connection object to interact with API
conn = AnaplanConnection(auth.get_auth_token(), "workspaceId", "modelId")

#Uploading a file
with open('file.csv', 'r') as file:
	data = file.read()
	anaplan.stream_upload(conn, "113000000116", data)
anaplan.stream_upload(conn, "113000000116", "", complete=True)

# Execute Anaplan action
#Returns a strint with task results and error dumps if any
print(ap.execute_action(conn, "actionId", retryCount))
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