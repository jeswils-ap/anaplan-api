.. anaplan-api documentation master file, created by
   sphinx-quickstart on Thu Dec 16 20:30:19 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

anaplan-api: Simple Interface for Anaplan Bulk API
===================================================

.. image:: https://img.shields.io/badge/license%20-BSD-green
    :target: https://opensource.org/licenses/BSD-2-Clause
    :alt: License Badge
.. image:: https://img.shields.io/badge/wheel-yes-green
    :target: https://pypi.org/project/anaplan-api/
    :alt: Wheel Support Badge
.. image:: https://img.shields.io/badge/Python-3.7%7C3.8%7C3.9%7C3.10-green
    :target: https://pypi.org/project/anaplan-api/
    :alt: Python Version Support Badge

**anaplan-api** is a simple interface for the latest version Anaplan Bulk API.

.. code-block:: python

   import logging
   from anaplan_api import anaplan
   from anaplan_api.AnaplanConnection import AnaplanConnection
   from anaplan_api.KeystoreManager import KeystoreManager

   logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',
                       level=logging.INFO)

   logger = logging.getLogger(__name__)

   if __name__ == '__main__':
       keys = KeystoreManager(path='/keystore.jks', passphrase='', alias='', key_pass='')

       auth = anaplan.generate_authorization(auth_type='Certificate', cert=keys.get_cert(), private_key=keys.get_key())
       conn = AnaplanConnection(authorization=auth, workspace_id='', model_id='')

       anaplan.file_upload(conn=conn, file_id="", chunk_size=5, data='/Users.csv')

       results = anaplan.execute_action(conn=conn, action_id="", retry_count=3)

       for result in results:
           if result: # Boolean check of ParserResponse object, true if failure dump is available
               print(result.get_error_dump())

**anaplan-api** allows you to easily interact with the latest version of Anaplan Bulk API and log those interactions.

Known Issues
------------
This library currently uses PyJKS library for handling Java Keystore files. This project does not appear to be actively
developed, and there is a known error installing pycryptodomex and twofish - both dependencies for PyJKS. The core files
required from this library are:

- jks.py
- rfc2898.py
- sun_crypto.py
- util.py

PyJKS Requirements
-------------------
- javaobj-py3
- pyasn1
- pyasn1_modules

You can simply download, remove the unnecessary files, and drop the jks folder in your site-package directory to work
around the error.

.. toctree::
   :maxdepth: 2

Contents
--------

.. toctree::
   anaplan_api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
