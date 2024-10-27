# Copyright 2023 Pexeso Inc. All rights reserved.

from .lib import _lib, _Pex_Status, _Pex_Lock
from pex.errors import Error


def mock_client(client):
    """
    Reinitializes a client so that it talks to the MockServer rather than the
    AE service.

    :param string client: the client that's going to be reinitialized
    :raise: :class:`Error` if the connection cannot be established
            or the provided authentication credentials are invalid.
    """
    with (
        _Pex_Lock.new(_lib) as c_lock,
        _Pex_Status.new(_lib) as c_status,
    ):
        _lib.Pex_Mockserver_InitClient(client._c_client.get(), None, c_status.get())
        Error.check_status(c_status)
