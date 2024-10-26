# Copyright 2023 Pexeso Inc. All rights reserved.

import ctypes
import json
from datetime import datetime
from collections import namedtuple
from enum import Enum

from pex.lib import (
    _lib,
    _Pex_Status,
    _Pex_Lock,
    _Pex_Buffer,
    _Pex_StartSearchRequest,
    _Pex_StartSearchResult,
    _Pex_CheckSearchRequest,
    _Pex_CheckSearchResult,
    _Pex_ListRequest,
    _Pex_ListResult,
)
from pex.errors import Error
from pex.client import _ClientType, _init_client
from pex.fingerprint import _Fingerprinter, FingerprintType


class PrivateSearchRequest(object):
    """
    Holds all data necessary to perform a private search. A search can only be
    performed using a fingerprint, but additional parameters may be supported
    in the future.
    """

    def __init__(self, fingerprint):
        self._fingerprint = fingerprint

    @property
    def fingerprint(self):
        """
        A fingerprint generated from a file or a byte buffer.

        :type: Fingerprint
        """
        return self._fingerprint

    def __repr__(self):
        return "PrivateSearchRequest(fingerprint=...)"


class PrivateSearchFuture(object):
    """
    This object is returned by the :meth:`PrivateSearchClient.start` method
    and is used to retrieve a search result.
    """

    def __init__(self, c_client, lookup_ids):
        self._raw_c_client = c_client.get()
        self._lookup_ids = lookup_ids

    def get(self):
        """
        Blocks until the search result is ready and then returns it.

        :raise: :class:`Error` if the search couldn't be performed, e.g.
                because of network issues.
        :rtype: PrivateSearchResult
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
        return "PrivateSearchFuture(lookup_ids={})".format(self._lookup_ids)


class ListEntriesRequest(object):
    """
    ListEntriesRequest must be passed to the :meth:`PrivateSearchClient.list_entries`
    method when listing all the ingested assets in the catalog. It allows the
    user to specify some options that will narrow the listing down which is
    important especially for large catalogs.
    """

    def __init__(self, after="", limit=0):
        self._after = after
        self._limit = limit

    def __repr__(self):
        return "ListEntriesRequest(after={}, limit={})".format(self._after, self._limit)


class Lister(object):
    """
    Lister is an object returned by the List() functions when listing all the
    ingested assets. It represents a sort of paginator that will allow the user
    to retrieve the entries in smaller chunks, which is important if the catalog
    contains too many entries.
    """

    def __init__(self, c_client, after, limit):
        self._c_client = c_client
        self._end_cursor = after
        self._limit = limit
        self._has_next_page = True

    @property
    def end_cursor(self):
        """
        A cursor that can be later passed when initializing :class:`ListEntriesRequest`.

        :type: str
        """
        return self._end_cursor

    @property
    def has_next_page(self):
        """
        This signifies whether there's a next page to be retrieved.

        :type: bool
        """
        return self._has_next_page

    def list(self):
        """
        This method grabs the next "page" and returns entries.

        :raise: :class:`Error` if the request couldn't complete, e.g.
                because of network issues.
        :rtype: list
        """
        with (
            _Pex_Lock.new(_lib) as c_lock,
            _Pex_Status.new(_lib) as c_status,
            _Pex_ListRequest.new(_lib) as c_req,
            _Pex_ListResult.new(_lib) as c_res,
        ):
            _lib.Pex_ListRequest_SetAfter(c_req.get(), self._end_cursor.encode())
            _lib.Pex_ListRequest_SetLimit(c_req.get(), self._limit)

            _lib.Pex_List(self._c_client.get(), c_req.get(), c_res.get(), c_status.get())
            Error.check_status(c_status)

            res = _lib.Pex_ListResult_GetJSON(c_res.get())
            j = json.loads(res)
            self._end_cursor = j['end_cursor']
            self._has_next_page = j['has_next_page']
            return j['entries']


class PrivateSearchClient(_Fingerprinter):
    def __init__(self, client_id, client_secret):
        self._c_client = _init_client(_ClientType.PRIVATE_SEARCH, client_id, client_secret)
        super().__init__(self._c_client)

    def start_search(self, req):
        """
        Starts a private search. This operation does not block until the
        search is finished, it does however perform a network operation to
        initiate the search on the backend service.

        :param PrivateSearchRequest req: search parameters.
        :raise: :class:`Error` if the search couldn’t be initiated, e.g.
                because of network issues.
        :rtype: PrivateSearchFuture
        """
        with (
            _Pex_Lock.new(_lib) as c_lock,
            _Pex_Status.new(_lib) as c_status,
            _Pex_Buffer.new(_lib) as c_ft,
            _Pex_StartSearchRequest.new(_lib) as c_req,
            _Pex_StartSearchResult.new(_lib) as c_res,
        ):
            _lib.Pex_Buffer_Set(c_ft.get(), req.fingerprint._ft, len(req.fingerprint._ft))

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

            return PrivateSearchFuture(self._c_client, lookup_ids)

    def ingest(self, provided_id, ft):
        with (
            _Pex_Lock.new(_lib) as c_lock,
            _Pex_Status.new(_lib) as c_status,
            _Pex_Buffer.new(_lib) as c_ft,
        ):
            _lib.Pex_Buffer_Set(c_ft.get(), ft._ft, len(ft._ft))

            _lib.Pex_Ingest(
                self._c_client.get(), provided_id.encode(), c_ft.get(), c_status.get()
            )
            Error.check_status(c_status)

    def archive(self, provided_id, ft_types=FingerprintType.ALL):
        with (
            _Pex_Lock.new(_lib) as c_lock,
            _Pex_Status.new(_lib) as c_status,
        ):
            _lib.Pex_Archive(
                self._c_client.get(), provided_id.encode(), int(ft_types), c_status.get()
            )
            Error.check_status(c_status)

    def list_entries(self, req):
        """
        This method initiates listing of the catalog and returns a Lister that can
        be used to retrieve the entries.
        """
        return Lister(self._c_client, req._after, req._limit)
