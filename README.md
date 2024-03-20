# anaplan-api

Anaplan-API is a Python library wrapper for [Anaplan Bulk API](https://anaplanbulkapi20.docs.apiary.io/) and [Anaplan Authentication API](https://anaplanauthentication.docs.apiary.io/).

## Installation

Use the package manager [pip](https://pypi.org/project/anaplan-api/) to install Anaplan-API.

```bash
pip3 install anaplan_api
```

## Usage

```python
import logging
from anaplan_api.anaplan import anaplan
from anaplan_api.anaplan.models.AnaplanConnection import AnaplanConnection
from anaplan_api.anaplan.KeystoreManager import KeystoreManager

logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    keys = KeystoreManager(path='/keystore.jks', passphrase='', alias='', key_pass='')
    
    auth = anaplan.authorize("Basic", email="user@mail.com", password="password")
    auth = anaplan.authorize("Certificate", private_key=keys.get_key(), certificate=keys.get_cert())
    conn = AnaplanConnection(auth, "WorkspaceID", "ModelID")

    anaplan.file_upload(conn=conn, file_id="", chunk_size=5, data='/Users.csv')

    results = anaplan.execute_action(conn=conn, action_id="", retry_count=3)

    for result in results:
        if result: # Boolean check of ParserResponse object, true if failure dump is available
            print(result.error_dump)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[BSD](https://opensource.org/licenses/BSD-2-Clause)
