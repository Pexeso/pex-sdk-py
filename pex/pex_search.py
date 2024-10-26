# Copyright 2023 Pexeso Inc. All rights reserved.

import ctypes
import json
from datetime import datetime
from collections import namedtuple
from enum import IntEnum

from pex.lib import (
    _lib,
    _Pex_Status,
    _Pex_Lock,
    _Pex_Buffer,
    _Pex_StartSearchRequest,
    _Pex_StartSearchResult,
    _Pex_CheckSearchRequest,
    _Pex_CheckSearchResult,
)
from pex.errors import Error
from pex.client import _ClientType, _init_client
from pex.fingerprint import _Fingerprinter


class PexSearchType(IntEnum):
    """
    PexSearchType can optionally be specified in the PexSearchRequest and will
    allow to retrieve results that are more relevant to the given use-case.
    """

    """
    A type of PexSearch that will return results that will
    help identify the music in the provided media file.
    """
    IDENTIFY_MUSIC = 1

    """
    FindMatches is a type of PexSearch that will return all assets that
    matched against the given media file.
    """
    FIND_MATCHES = 2


class PexSearchRequest(object):
    """
    Holds all data necessary to perform a pex search.
    """

    def __init__(self, fingerprint, type=PexSearchType.IDENTIFY_MUSIC):
        """
        Constructor.

        :param Fingerprint fingerprint: A fingerprint previously generated from a file or a byte buffer.
        :param PexSearchType type: A type of the pex search performed
        """
        self._fingerprint = fingerprint
        self._type = type

    def __repr__(self):
        return f"PexSearchRequest(fingerprint=...,type={self._type.name})"


class PexSearchFuture(object):
    """
    This object is returned by the :meth:`PexSearch.start` method
    and is used to retrieve a search result.
    """

    def __init__(self, client, lookup_ids):
        self._raw_c_client = client.get()
        self._lookup_ids = lookup_ids

    def get(self):
        """
        Blocks until the search result is ready and then returns it.

        :raise: :class:`Error` if the search couldn't be performed, e.g.
                because of network issues.
        :rtype: dict
        """
        with (
            _Pex_Lock.new(_lib) as c_lock,
            _Pex_Status.new(_lib) as c_status,
            _Pex_CheckSearchRequest.new(_lib) as c_req,
            _Pex_CheckSearchResult.new(_lib) as c_res,
        ):
            for lookup_id in self._lookup_ids:
                _lib.Pex_CheckSearchRequest_AddLookupID(
                    c_req.get(), lookup_id.encode()
                )

            _lib.Pex_CheckSearch(
                self._raw_c_client, c_req.get(), c_res.get(), c_status.get()
            )
            Error.check_status(c_status)

            res = _lib.Pex_CheckSearchResult_GetJSON(c_res.get())
            j = json.loads(res)
            j['lookup_ids'] = self._lookup_ids
            return j

    @property
    def lookup_ids(self):
        """
        A list of IDs that uniquely identify a particular search. Can be
        used for diagnostics.

        :type: List[str]
        """
        return self._lookup_ids

    def __repr__(self):
        return f"PexSearchFuture(lookup_ids={self._lookup_ids})"


class PexSearchClient(_Fingerprinter):
    def __init__(self, client_id, client_secret):
        self._c_client = _init_client(_ClientType.PEX_SEARCH, client_id, client_secret)
        super().__init__(self._c_client)

    def start_search(self, req):
        """
        Starts a Pex search. This operation does not block until the
        search is finished, it does however perform a network operation to
        initiate the search on the backend service.

        :param PexSearchRequest req: search parameters.
        :raise: :class:`Error` if the search couldn’t be initiated, e.g.
                because of network issues.
        :rtype: PexSearchFuture
        """
        with (
            _Pex_Lock.new(_lib) as c_lock,
            _Pex_Status.new(_lib) as c_status,
            _Pex_Buffer.new(_lib) as c_ft,
            _Pex_StartSearchRequest.new(_lib) as c_req,
            _Pex_StartSearchResult.new(_lib) as c_res,
        ):
            _lib.Pex_Buffer_Set(c_ft.get(), req._fingerprint._ft, len(req._fingerprint._ft))

            _lib.Pex_StartSearchRequest_SetType(c_req.get(), req._type)
            _lib.Pex_StartSearchRequest_SetFingerprint(
                c_req.get(), c_ft.get(), c_status.get()
            )
            Error.check_status(c_status)

            _lib.Pex_StartSearch(
                self._c_client.get(), c_req.get(), c_res.get(), c_status.get()
            )
            Error.check_status(c_status)

            lookup_ids = list()
            c_lookup_id_pos = ctypes.c_size_t(0)
            c_lookup_id = ctypes.c_char_p()

            while _lib.Pex_StartSearchResult_NextLookupID(
                c_res.get(),
                ctypes.byref(c_lookup_id_pos),
                ctypes.byref(c_lookup_id)
            ):
                lookup_ids.append(c_lookup_id.value.decode())

            return PexSearchFuture(self._c_client, lookup_ids)
