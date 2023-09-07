# Copyright 2020 Pexeso Inc. All rights reserved.

import ctypes
from datetime import datetime
from collections import namedtuple
from enum import Enum

from pexae.lib import (
    _lib,
    _AE_Status,
    _AE_Lock,
    _AE_Buffer,
    _AE_PrivateSearchStartRequest,
    _AE_PrivateSearchStartResult,
    _AE_PrivateSearchCheckRequest,
    _AE_PrivateSearchCheckResult,
    _AE_PrivateSearchMatch,
)
from pexae.errors import AEError
from pexae.common import SegmentType, Segment


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

    def __init__(self, lookup_id, matches):
        self._lookup_id = lookup_id
        self._matches = matches

    @property
    def lookup_id(self):
        """
        An ID that uniquely identifies a particular search. Can be used for
        diagnostics.

        :type: int
        """
        return self._lookup_id

    @property
    def matches(self):
        """
        A list of :class:`PrivateSearchMatch`.

        :type: list
        """
        return self._matches

    def to_json(self):
        return {
            "LookupID": self._lookup_id,
            "Matches": [m.to_json() for m in self._matches],
        }

    @classmethod
    def from_json(cls, j):
        lookup_id = j.get("LookupID", "")
        matches = []
        if j.get("Matches") is not None:
            matches = [PrivateSearchMatch.from_json(s) for s in j["Matches"]]
        return PrivateSearchResult(lookup_id, matches)

    def __repr__(self):
        return "PrivateSearchResult(lookup_id={},matches=<{} objects>)".format(
            self.lookup_id, len(self.matches)
        )


class PrivateSearchFuture(object):
    """
    This object is returned by the :meth:`PrivateSearch.start` method
    and is used to retrieve a search result.
    """

    def __init__(self, client, lookup_id):
        self._raw_c_client = client._c_client.get()
        self._lookup_id = lookup_id

    def get(self):
        """
        Blocks until the search result is ready and then returns it.

        :raise: :class:`AEError` if the search couldn't be performed, e.g.
                because of network issues.
        :rtype: PrivateSearchResult
        """

        lock = _AE_Lock.new(_lib)

        c_status = _AE_Status.new(_lib)
        c_req = _AE_PrivateSearchCheckRequest.new(_lib)
        c_res = _AE_PrivateSearchCheckResult.new(_lib)

        _lib.AE_PrivateSearchCheckRequest_SetLookupID(
            c_req.get(), self._lookup_id.encode(), c_status.get()
        )
        AEError.check_status(c_status)

        _lib.AE_PrivateSearch_Check(
            self._raw_c_client, c_req.get(), c_res.get(), c_status.get()
        )
        AEError.check_status(c_status)

        c_match = _AE_PrivateSearchMatch.new(_lib)
        c_matches_pos = ctypes.c_int(0)

        matches = []
        while _lib.AE_PrivateSearchCheckResult_NextMatch(
            c_res.get(), c_match.get(), ctypes.byref(c_matches_pos)
        ):
            matches.append(
                PrivateSearchMatch(
                    provided_id=_lib.AE_PrivateSearchMatch_GetProvidedID(
                        c_match.get()).decode() ,
                    segments=_extract_private_search_segments(c_match),
                )
            )

        return PrivateSearchResult(
            lookup_id=_lib.AE_PrivateSearchCheckResult_GetLookupID(
                c_res.get()
            ).decode(),
            matches=matches,
        )

    @property
    def lookup_id(self):
        """
        An ID that uniquely identifies a particular search. Can be used for
        diagnostics.

        :type: str
        """
        return self._lookup_id

    def __repr__(self):
        return "PrivateSearchFuture(lookup_id={})".format(self._lookup_id)


def _start_private_search(client, req):
    """
    Starts a private search. This operation does not block until the
    search is finished, it does however perform a network operation to
    initiate the search on the backend service.

    :param PrivateSearchRequest req: search parameters.
    :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
            because of network issues.
    :rtype: PrivateSearchFuture
    """

    lock = _AE_Lock.new(_lib)

    c_status = _AE_Status.new(_lib)
    c_ft = _AE_Buffer.new(_lib)
    c_req = _AE_PrivateSearchStartRequest.new(_lib)
    c_res = _AE_PrivateSearchStartResult.new(_lib)

    _lib.AE_Buffer_Set(c_ft.get(), req.fingerprint._ft, len(req.fingerprint._ft))

    _lib.AE_PrivateSearchStartRequest_SetFingerprint(
        c_req.get(), c_ft.get(), c_status.get()
    )
    AEError.check_status(c_status)

    _lib.AE_PrivateSearch_Start(
        client._c_client.get(), c_req.get(), c_res.get(), c_status.get()
    )
    AEError.check_status(c_status)

    lookup_id = _lib.AE_PrivateSearchStartResult_GetLookupID(c_res.get()).decode()
    return PrivateSearchFuture(client, lookup_id)


def _ingest_private_search_asset(client, provided_id, ft):
    lock = _AE_Lock.new(_lib)

    c_status = _AE_Status.new(_lib)
    c_ft = _AE_Buffer.new(_lib)

    _lib.AE_Buffer_Set(c_ft.get(), ft._ft, len(ft._ft))

    _lib.AE_PrivateSearch_Ingest(
        client._c_client.get(), provided_id.encode(), c_ft.get(), c_status.get()
    )
    AEError.check_status(c_status)


def _extract_private_search_segments(c_match):
    c_query_start = ctypes.c_int64(0)
    c_query_end = ctypes.c_int64(0)
    c_asset_start = ctypes.c_int64(0)
    c_asset_end = ctypes.c_int64(0)
    c_type = ctypes.c_int(0)
    c_segments_pos = ctypes.c_int(0)

    segments = []
    while _lib.AE_PrivateSearchMatch_NextSegment(
        c_match.get(),
        ctypes.byref(c_query_start),
        ctypes.byref(c_query_end),
        ctypes.byref(c_asset_start),
        ctypes.byref(c_asset_end),
        ctypes.byref(c_type),
        ctypes.byref(c_segments_pos),
    ):
        segments.append(
            Segment(
                typ=SegmentType(c_type.value),
                query_start=c_query_start.value,
                query_end=c_query_end.value,
                asset_start=c_asset_start.value,
                asset_end=c_asset_end.value,
            )
        )
    return segments
