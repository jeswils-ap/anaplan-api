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
from AnaplanConnection import AnaplanConnection

#Generate auth token for API requests
auth = ap.generate_authorization('basic', 'user', 'password')

# Create connection object to interact with API
conn = AnaplanConnection(auth, "workspaceId", "modelId")

# Execute Anaplan action
ap.execute_action(conn, "actionId", retryCount)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[BSD](https://opensource.org/licenses/BSD-2-Clause)