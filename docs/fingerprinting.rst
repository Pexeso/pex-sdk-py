###############################################################################
Fingerprinting
###############################################################################

A fingerprint is how the SDK identifies a piece of digital content. It can be
generated from a media file or from a memory buffer. The content must be
encoded in one of the supported formats and must be longer than 1 second.

Supported formats:

:Audio: aac
:Video: h264, h265

Example (creating a fingerprint from a file):

.. code-block:: python

    import pex

    try:
        client = pex.NewClient("client01", "secret01")
        ft1 = client.fingerprint_file("/path/to/file1.mp4")

        ft_types = pex.FingerprintType.VIDEO | pex.FingerprintType.MELODY
        ft2 = client.fingerprint_file("/path/to/file2.mp4", ft_types)
        # ...
    except pex.AEError as err:
        pass  # handle error

Example (creating a fingerprint from a byte buffer):

.. code-block:: python

    import pex

    try:
        client = pex.NewClient("client01", "secret01")
        with open("/path/to/file1.mp4", "rb") as fp:
            ft = client.fingerprint_buffer(fp.read())

        with open("/path/to/file2.mp4", "rb") as fp:
            ft = client.fingerprint_buffer(fp.read(), pex.FingerprintType.AUDIO)

        # ...
    except pex.AEError as err:
        pass  # handle error

.. warning::

    Keep in mind that generating a fingerprint is a CPU bound operation and might
    consume a significant amount of your CPU time.
