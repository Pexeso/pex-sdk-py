# Copyright 2023 Pexeso Inc. All rights reserved.

import ctypes
from enum import IntEnum

from .lib import _lib, _Pex_Client, _Pex_Status, _Pex_Lock
from pex.errors import Error, Code


class _ClientType(IntEnum):
    PRIVATE_SEARCH = 0
    PEX_SEARCH = 1


def _init_client(client_type, client_id, client_secret):
    c_status_code = ctypes.c_int(0)
    c_status_message = ctypes.create_string_buffer(100)
    c_status_message_size = ctypes.sizeof(c_status_message)

    _lib.Pex_Init(client_id.encode(), client_secret.encode(),
                  ctypes.byref(c_status_code),
                  c_status_message, c_status_message_size)
    Error.check(c_status_code.value, c_status_message.value.decode())

    with (
        _Pex_Lock.new(_lib) as c_lock,
        _Pex_Status.new(_lib) as c_status,
    ):
        c_client = _Pex_Client.new(_lib)
        c_client.init()

        _lib.Pex_Client_Init(c_client.get(), client_type.value, client_id.encode(),
                             client_secret.encode(), c_status.get())
        status = Error.from_status(c_status)
        if status.code != Code.OK:
            raise status
        return c_client
