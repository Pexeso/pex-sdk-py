# Copyright 2020 Pexeso Inc. All rights reserved.

from .lib import _lib, _AE_Status, _AE_Lock
from pexae.errors import AEError


def mock_client(client):
    """
    Reinitializes a client so that it talks to the MockServer rather than the
    AE service.

    :param string client: the client that's going to be reinitialized
    :raise: :class:`AEError` if the connection cannot be established
            or the provided authentication credentials are invalid.
    """

    lock = _AE_Lock.new(_lib)

    c_status = _AE_Status.new(_lib)
    _lib.AE_Mockserver_InitClient(client._c_client.get(), None, c_status.get())
    AEError.check_status(c_status)
