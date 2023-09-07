.. _client:

################################################################################
Mockserver
################################################################################

Mockserver is a testing server preloaded with some test data that will help you
write, debug and test your applications. The :func:`pexae.mock_client`
function initializes an existing client for use with the mockserver.

More information can be found in the official `Mockserver documentation`_.

.. _Mockserver documentation: https://docs.ae.pex.com/mockserver/

.. code-block:: python

    try:
        client = pexae.Client("client01", "secret01")
        pexae.MockClient(client)
    except pexae.AEError as err:
        pass  # handle error


********************************************************************************
API reference
********************************************************************************

.. autofunction:: pexae.mock_client
