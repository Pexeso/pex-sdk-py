.. _client:

################################################################################
Mockserver
################################################################################

Mockserver is a testing server preloaded with some test data that will help you
write, debug and test your applications. The :func:`pex.mock_client`
function initializes an existing client for use with the mockserver.

More information can be found in the official `Mockserver documentation`_.

.. _Mockserver documentation: https://docs.ae.pex.com/mockserver/

.. code-block:: python

    try:
        client = pex.Client("client01", "secret01")
        pex.MockClient(client)
    except pex.AEError as err:
        pass  # handle error


********************************************************************************
API reference
********************************************************************************

.. autofunction:: pex.mock_client
