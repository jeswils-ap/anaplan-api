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
    
    auth = anaplan.authorize("Basic", email="{user@mail.com}", password="{password}")
    auth = anaplan.authorize("Certificate", certificate=keys.get_cert(), private_key=keys.get_key(), password=b"{key_password}")
    conn = AnaplanConnection(auth.auth_token, "{workspace_id}", "{model_id}")

    anaplan.file_upload(conn=conn, file_id="{file_id}", chunk_size=5, data='/Users.csv')

    results = anaplan.execute_action(conn=conn, action_id="", retry_count=3)

    for result in results.responses:
        print(result.task_details)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[BSD](https://opensource.org/licenses/BSD-2-Clause)
