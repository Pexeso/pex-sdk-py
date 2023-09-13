# Copyright 2023 Pexeso Inc. All rights reserved.

import ctypes
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
    _Pex_SearchMatch,
)
from pex.errors import Error
from pex.common import SegmentType, Segment, _extract_segments
from pex.client import _ClientType, _init_client
from pex.fingerprint import _Fingerprinter


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


class PrivateSearchMatch(object):
    """
    Contains detailed information about the match, including information about
    the matched asset, and the matching segments.
    """

    def __init__(self, provided_id, segments):
        self._provided_id = provided_id
        self._segments = segments

    @property
    def provided_id(self):
        """
        The ID provided during ingestion.

        :type: str
        """
        return self._provided_id

    @property
    def segments(self):
        """
        A list of matching :class:`Segment` instances.

        :type: list
        """
        return self._segments

    def to_json(self):
        return {
            "ProvidedID": self._provided_id,
            "Segments": [s.to_json() for s in self._segments],
        }

    @classmethod
    def from_json(cls, j):
        segments = [Segment.from_json(s) for s in j["Segments"]]
        return PrivateSearchMatch(j["ProvidedID"], segments)

    def __repr__(self):
        return "PrivateSearchMatch(provided_id={},segments={})".format(
            self.provided_id, self.segments
        )


class PrivateSearchResult(object):
    """
    This object is returned from :meth:`PrivateSearchFuture.get` upon
    successful comptetion.
    """

    def __init__(self, lookup_ids, matches):
        self._lookup_ids = lookup_ids
        self._matches = matches

    @property
    def lookup_ids(self):
        """
        A list of IDs that uniquely identify a particular search. Can be
        used for diagnostics.

        :type: List[str]
        """
        return self._lookup_ids

    @property
    def matches(self):
        """
        A list of :class:`PrivateSearchMatch`.

        :type: list
        """
        return self._matches

    def to_json(self):
        return {
            "LookupIDs": self._lookup_ids,
            "Matches": [m.to_json() for m in self._matches],
        }

    @classmethod
    def from_json(cls, j):
        lookup_ids = j.get("LookupIDs", "")
        matches = []
        if j.get("Matches") is not None:
            matches = [PrivateSearchMatch.from_json(s) for s in j["Matches"]]
        return PrivateSearchResult(lookup_ids, matches)

    def __repr__(self):
        return "PrivateSearchResult(lookup_ids={},matches=<{} objects>)".format(
            self.lookup_ids, len(self.matches)
        )


class PrivateSearchFuture(object):
    """
    This object is returned by the :meth:`PrivateSearch.start` method
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

        lock = _Pex_Lock.new(_lib)

        c_status = _Pex_Status.new(_lib)
        c_req = _Pex_CheckSearchRequest.new(_lib)
        c_res = _Pex_CheckSearchResult.new(_lib)

        for lookup_id in self._lookup_ids:
            _lib.Pex_CheckSearchRequest_AddLookupID(
                c_req.get(), lookup_id.encode()
            )

        _lib.Pex_CheckSearch(
            self._raw_c_client, c_req.get(), c_res.get(), c_status.get()
        )
        Error.check_status(c_status)

        c_match = _Pex_SearchMatch.new(_lib)
        c_matches_pos = ctypes.c_int(0)

        matches = []
        while _lib.Pex_CheckSearchResult_NextMatch(
            c_res.get(), c_match.get(), ctypes.byref(c_matches_pos)
        ):
            provided_id = _lib.Pex_SearchMatch_GetProvidedID(c_match.get(), c_status.get())
            Error.check_status(c_status)

            matches.append(
                PrivateSearchMatch(
                    provided_id=provided_id.decode(),
                    segments=_extract_segments(c_match),
                )
            )

        return PrivateSearchResult(
            lookup_ids=self._lookup_ids,
            matches=matches,
        )

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


class PrivateSearchClient(_Fingerprinter):
    def __init__(self, client_id, client_secret):
        self._c_client = _init_client(_ClientType.PRIVATE_SEARCH, client_id, client_secret)

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

        lock = _Pex_Lock.new(_lib)

        c_status = _Pex_Status.new(_lib)
        c_ft = _Pex_Buffer.new(_lib)
        c_req = _Pex_StartSearchRequest.new(_lib)
        c_res = _Pex_StartSearchResult.new(_lib)

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
        lock = _Pex_Lock.new(_lib)

        c_status = _Pex_Status.new(_lib)
        c_ft = _Pex_Buffer.new(_lib)

        _lib.Pex_Buffer_Set(c_ft.get(), ft._ft, len(ft._ft))

        _lib.Pex_Ingest(
            self._c_client.get(), provided_id.encode(), c_ft.get(), c_status.get()
        )
        Error.check_status(c_status)
