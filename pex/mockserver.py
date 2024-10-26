# Copyright 2023 Pexeso Inc. All rights reserved.

from .lib import _lib, _Pex_Status, _Pex_Lock
from pex.errors import Error


def mock_client(client):
    # We used to have a mock server here, but it is no longer supported.
    pass
