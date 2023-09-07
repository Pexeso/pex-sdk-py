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
    _AE_Asset,
    _AE_MetadataSearchStartRequest,
    _AE_MetadataSearchStartResult,
    _AE_MetadataSearchCheckRequest,
    _AE_MetadataSearchCheckResult,
    _AE_MetadataSearchMatch,
)
from pexae.errors import AEError
from pexae.common import SegmentType, Segment
from pexae.asset import Asset, _extract_asset


class MetadataSearchRequest(object):
    """
    Holds all data necessary to perform a metadata search. A search can only be
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
        return "MetadataSearchRequest(fingerprint=...)"


class MetadataSearchMatch(object):
    """
    Contains detailed information about the match, including information about
    the matched asset, and the matching segments.
    """

    def __init__(self, asset, segments):
        self._asset = asset
        self._segments = segments

    @property
    def asset(self):
        """
        The asset whose fingerprint matches the query.

        :type: Asset
        """
        return self._asset

    @property
    def segments(self):
        """
        A list of matching :class:`Segment` instances.

        :type: list
        """
        return self._segments

    def to_json(self):
        return {
            "Asset": self._asset.to_json(),
            "Segments": [s.to_json() for s in self._segments],
        }

    @classmethod
    def from_json(cls, j):
        asset = Asset.from_json(j["Asset"])
        segments = [Segment.from_json(s) for s in j["Segments"]]
        return MetadataSearchMatch(asset, segments)

    def __repr__(self):
        return "MetadataSearchMatch(asset={},segments={})".format(
            self.asset, self.segments
        )


class MetadataSearchResult(object):
    """
    This object is returned from :meth:`MetadataSearchFuture.get` upon
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
        A list of :class:`MetadataSearchMatch`.

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
        lookup_id = j["LookupID"]
        matches = []
        if j.get("Matches") is not None:
            matches = [MetadataSearchMatch.from_json(s) for s in j["Matches"]]
        return MetadataSearchResult(lookup_id, matches)

    def __repr__(self):
        return "MetadataSearchResult(lookup_id={},matches=<{} objects>)".format(
            self.lookup_id, len(self.matches)
        )


class MetadataSearchFuture(object):
    """
    This object is returned by the :meth:`MetadataSearch.start` method
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
        :rtype: MetadataSearchResult
        """

        lock = _AE_Lock.new(_lib)

        c_status = _AE_Status.new(_lib)
        c_req = _AE_MetadataSearchCheckRequest.new(_lib)
        c_res = _AE_MetadataSearchCheckResult.new(_lib)

        _lib.AE_MetadataSearchCheckRequest_SetLookupID(
            c_req.get(), self._lookup_id.encode(), c_status.get()
        )
        AEError.check_status(c_status)

        _lib.AE_MetadataSearch_Check(
            self._raw_c_client, c_req.get(), c_res.get(), c_status.get()
        )
        AEError.check_status(c_status)

        c_match = _AE_MetadataSearchMatch.new(_lib)
        c_matches_pos = ctypes.c_int(0)

        c_asset = _AE_Asset.new(_lib)

        matches = []
        while _lib.AE_MetadataSearchCheckResult_NextMatch(
            c_res.get(), c_match.get(), ctypes.byref(c_matches_pos)
        ):
            _lib.AE_MetadataSearchMatch_GetAsset(c_match.get(), c_asset.get())

            matches.append(
                MetadataSearchMatch(
                    asset=_extract_asset(c_asset),
                    segments=_extract_metadata_search_segments(c_match),
                )
            )

        return MetadataSearchResult(
            lookup_id=_lib.AE_MetadataSearchCheckResult_GetLookupID(
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
        return "MetadataSearchFuture(lookup_id={})".format(self._lookup_id)


def _start_metadata_search(client, req):
    """
    Starts a metadata search. This operation does not block until the
    search is finished, it does however perform a network operation to
    initiate the search on the backend service.

    :param MetadataSearchRequest req: search parameters.
    :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
            because of network issues.
    :rtype: MetadataSearchFuture
    """

    lock = _AE_Lock.new(_lib)

    c_status = _AE_Status.new(_lib)
    c_ft = _AE_Buffer.new(_lib)
    c_req = _AE_MetadataSearchStartRequest.new(_lib)
    c_res = _AE_MetadataSearchStartResult.new(_lib)

    _lib.AE_Buffer_Set(c_ft.get(), req.fingerprint._ft, len(req.fingerprint._ft))

    _lib.AE_MetadataSearchStartRequest_SetFingerprint(
        c_req.get(), c_ft.get(), c_status.get()
    )
    AEError.check_status(c_status)

    _lib.AE_MetadataSearch_Start(
        client._c_client.get(), c_req.get(), c_res.get(), c_status.get()
    )
    AEError.check_status(c_status)

    lookup_id = _lib.AE_MetadataSearchStartResult_GetLookupID(c_res.get()).decode()
    return MetadataSearchFuture(client, lookup_id)


def _extract_metadata_search_segments(c_match):
    c_query_start = ctypes.c_int64(0)
    c_query_end = ctypes.c_int64(0)
    c_asset_start = ctypes.c_int64(0)
    c_asset_end = ctypes.c_int64(0)
    c_type = ctypes.c_int(0)
    c_segments_pos = ctypes.c_int(0)

    segments = []
    while _lib.AE_MetadataSearchMatch_NextSegment(
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
