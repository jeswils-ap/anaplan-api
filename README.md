# anaplan-api

Anaplan-API is a Python library wrapper for [Anaplan Bulk API](https://anaplanbulkapi20.docs.apiary.io/) and [Anaplan Authentication API](https://anaplanauthentication.docs.apiary.io/).

## Installation

Use the package manager [pip](https://pypi.org/project/anaplan-api/) to install Anaplan-API.

```bash
pip install anaplan_api
```

## Usage

```python
import anaplan_api as ap
from anaplan_api.AuthToken import AuthToken
from anaplan_api.KeystoreManager import KeystoreManager
from anaplan_api.AnaplanConnection import AnaplanConnection

# Generate Basic Auth token for API requests
auth = ap.generate_authorization('Basic', 'user', 'password')

# Generate Cert Auth token for API requests
keys = KeystoreManager('/path/to/keystore.jks', 'keystore_pass', 'key_alias', 'private_key_passphrase')
priv_key = keys.get_key()
pub_cert = keys.get_cert()
auth_req = ap.generate_authorization('Certificate', pub_cert, priv_key)

auth = AuthToken(authReq[0], authReq[1])

# Create connection object to interact with API
conn = AnaplanConnection(auth.get_auth_token(), "workspaceId", "modelId")

# Uploading a file
with open('file.csv', 'r') as file:
	data = file.read()
	ap.file_upload(conn, "113000000116", 5, data)

# Execute Anaplan action
# Returns a strint with task results and error dumps if any
result_arr = anaplan.execute_action(conn, "118000000007", 3)

# 
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