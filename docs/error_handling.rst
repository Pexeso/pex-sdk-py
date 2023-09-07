################################################################################
Error handling
################################################################################

All error handling in the SDK is done by raising an instance of
:class:`~pexae.AEError`. Each error is identified by a code that can help you
understand why the error was raised in the first place.

Example:


.. code-block:: python

    import pexae

    try:
        ft = client.fingerprint_file("/path/to/file.mp4")
        # ...
    except pexae.AEError as err:
        if err.code == pexae.Code.INVALID_INPUT:
            print("the file is invalid")
        # ...


********************************************************************************
API reference
********************************************************************************

.. autoclass:: pexae.Code()

.. autoclass:: pexae.AEError()

