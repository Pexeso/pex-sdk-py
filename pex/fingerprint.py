# Copyright 2023 Pexeso Inc. All rights reserved.

from enum import IntEnum
import ctypes

from pex.lib import _lib, _Pex_Status, _Pex_Buffer, _Pex_Lock
from pex.errors import Error


class FingerprintType(IntEnum):
    """
    FingerprintType is a bit flag used to specify a subset of fingerprint types.
    """
    VIDEO = 1
    AUDIO = 2
    MELODY = 4
    ALL = VIDEO | AUDIO | MELODY


class Fingerprint(object):
    """
    Fingerprint is how the SDK identifies a piece of digital content.  It can
    be generated from a media file or from a memory buffer. The content must be
    encoded in one of the supported formats and must be longer than 1 second.
    """

    def __init__(self, ft):
        self._ft = ft


class _Fingerprinter(object):
    def __init(self, c_client):
        self._c_client = c_client

    def fingerprint_file(self, path, ft_types=FingerprintType.ALL):
        """
        Generate a fingerprint from a file stored on a disk. The parameter to
        the function must be a path to a valid file in supported format.

        :param str path: path to the media file we're trying to fingerprint.
        :raise: :class:`Error` if the media file is missing or invalid.
        :rtype: Fingerprint
        """
        lk = _Pex_Lock.new(_lib)

        c_ft = _Pex_Buffer.new(_lib)
        c_status = _Pex_Status.new(_lib)

        _lib.Pex_FingerprintFile(self._c_client.get(), path.encode(), c_ft.get(),
                                 c_status.get(), int(ft_types))
        Error.check_status(c_status)

        data = _lib.Pex_Buffer_GetData(c_ft.get())
        size = _lib.Pex_Buffer_GetSize(c_ft.get())
        ft = ctypes.string_at(data, size)
        return Fingerprint(ft)

    def fingerprint_buffer(self, buf, ft_types=FingerprintType.ALL):
        """
        Generate a fingerprint from a media file loaded in memory as a byte
        buffer.

        :param bytes buf: A byte buffer holding a media file.
        :raise: :class:`Error` if the buffer holds invalid data.
        :rtype: Fingerprint
        """

        lk = _Pex_Lock.new(_lib)

        c_status = _Pex_Status.new(_lib)
        c_buf = _Pex_Buffer.new(_lib)
        c_ft = _Pex_Buffer.new(_lib)

        _lib.Pex_Buffer_Set(c_buf.get(), buf, len(buf))

        _lib.Pex_FingerprintBuffer(self._c_client.get(), c_buf.get(),
                                   c_ft.get(), c_status.get(), int(ft_types))
        Error.check_status(c_status)

        data = _lib.Pex_Buffer_GetData(c_ft.get())
        size = _lib.Pex_Buffer_GetSize(c_ft.get())
        ft = ctypes.string_at(data, size)
        return Fingerprint(ft)

