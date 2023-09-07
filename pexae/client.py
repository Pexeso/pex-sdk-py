# Copyright 2020 Pexeso Inc. All rights reserved.

import ctypes
from enum import IntEnum

from .lib import _lib, _AE_Client, _AE_Status, _AE_Lock
from pexae.license_search import _start_license_search
from pexae.metadata_search import _start_metadata_search
from pexae.private_search import _start_private_search, _ingest_private_search_asset
from pexae.fingerprint import _Fingerprinter
from pexae.errors import AEError


class _ClientType(IntEnum):
    LICENSE_SEARCH = 0
    PEX_SEARCH = 1


def _init_client(client_type, client_id, client_secret):
    c_status_code = ctypes.c_int(0)
    c_status_message = ctypes.create_string_buffer(100)
    c_status_message_size = ctypes.sizeof(c_status_message)

    _lib.AE_Init(client_id.encode(), client_secret.encode(),
                 ctypes.byref(c_status_code),
                 c_status_message, c_status_message_size)
    AEError.check(c_status_code.value, c_status_message.value.decode())

    lock = _AE_Lock.new(_lib)

    c_status = _AE_Status.new(_lib)
    c_client = _AE_Client.new(_lib)

    _lib.AE_Client_InitType(c_client.get(), client_type.value, client_id.encode(),
                            client_secret.encode(), c_status.get())
    AEError.check_status(c_status)
    # TODO: if this raises, run AE_Cleanup
    return c_client


class Client(_Fingerprinter):
    """
    This class serves as an entry point to all operations that
    communicate with the Attribution Engine backend service. It
    automatically handles the connection and authentication with the
    service.
    """

    def __init__(self, client_id, client_secret):
        self._c_client = _init_client(_ClientType.LICENSE_SEARCH, client_id, client_secret)

    def start_license_search(self, req):
        """
        Starts a license search. This operation does not block until the
        search is finished, it does however perform a network operation to
        initiate the search on the backend service.

        :param LicenseSearchRequest req: search parameters.
        :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
                because of network issues.
        :rtype: LicenseSearchFuture
        """
        return _start_license_search(self, req)

    def start_metadata_search(self, req):
        """
        Starts a metadata search. This operation does not block until the
        search is finished, it does however perform a network operation to
        initiate the search on the backend service.

        :param MetadataSearchRequest req: search parameters.
        :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
                because of network issues.
        :rtype: MetadataSearchFuture
        """
        return _start_metadata_search(self, req)

    def start_private_search(self, req):
        """
        Starts a private search. This operation does not block until the
        search is finished, it does however perform a network operation to
        initiate the search on the backend service.

        :param PrivateSearchRequest req: search parameters.
        :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
                because of network issues.
        :rtype: PrivateSearchFuture
        """
        return _start_private_search(self, req)

    def ingest_private_search_asset(self, provided_id, ft):
        """
        Ingests a fingerprint into the private search catalog. The catalog is
        determined from the authentication credentials used when initializing
        the client. If you want to ingest into multiple catalogs within one
        application, you need to use multiple clients. The id parameter
        identifies the fingerprint and will be returned during search to
        identify the matched asset.

        :param string provided_id: unique id that identifies the ingested fingerprint.
        :param Fingerprint ft: fingerprint to ingest.
        :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
                because of network issues.
        """
        return _ingest_private_search_asset(self, provided_id, ft)
