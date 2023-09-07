.. _client:

################################################################################
Client
################################################################################

In order to do anything that communicates with the backend service, e.g.
performing a search or retrieving information about an asset, you first need to
initialize a client and authenticate:

.. code-block:: python

    try:
        client = pexae.Client("client01", "secret01")
    except pexae.AEError as err:
        pass  # handle error


********************************************************************************
API reference
********************************************************************************

.. autoclass:: pexae.Client()
   :members:
