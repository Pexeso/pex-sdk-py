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
    _AE_StartSearchRequest,
    _AE_StartSearchResult,
    _AE_CheckSearchRequest,
    _AE_CheckSearchResult,
    _AE_SearchMatch,
)
from pexae.errors import AEError
from pexae.common import SegmentType, Segment
from pexae.client import _ClientType, _init_client
from pexae.fingerprint import _Fingerprinter


class PexSearchAsset(object):
    """
    This class represents a pex search asset and the data associated with it.
    """

    def __init__(self, isrc, label, title, artist, duration):
        self._isrc = isrc
        self._label = label
        self._title = title
        self._artist = artist
        self._duration = duration

    @property
    def isrc(self):
        """
        The ISRC of the asset.

        :type: str
        """
        return self._isrc

    @property
    def label(self):
        """
        The label that owns the asset.

        :type: str
        """
        return self._label

    @property
    def title(self):
        """
        The title of the asset.

        :type: str
        """
        return self._title

    @property
    def artist(self):
        """
        The artist who contributed to the asset.

        :type: list
        """
        return self._artist

    @property
    def duration(self):
        """
        The duration of the asset.

        :type: float
        """
        return self._duration

    def to_json(self):
        return {
            "ISRC": self._isrc,
            "Label": self._label,
            "Title": self._title,
            "Artist": self._artist,
            "Duration": round(self._duration),
        }

    @classmethod
    def from_json(cls, j):
        asset_isrc = j["ISRC"]
        asset_label= j["Label"]
        asset_title = j["Title"]
        asset_artist = j["Artist"]
        asset_duration = j["Duration"]
        return PexSearchAsset(asset_isrc, asset_label, asset_title, asset_artist, asset_duration)

    def __repr__(self):
        return "Asset(isrc={},title={},artist={},duration={})".format(
            self.isrc, self.title, self.artist, self.duration
        )

    @staticmethod
    def extract(c_asset):
        return PexSearchAsset(
            isrc=_lib.AE_Asset_GetISRC(c_asset.get()).decode(),
            label=_lib.AE_Asset_GetLabel(c_asset.get()).decode(),
            title=_lib.AE_Asset_GetTitle(c_asset.get()).decode(),
            artist=_lib.AE_Asset_GetArtist(c_asset.get()).decode(),
            duration=_lib.AE_Asset_GetDuration(c_asset.get()),
        )

class PexSearchRequest(object):
    """
    Holds all data necessary to perform a pex search. A search can only be
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
        return "PexSearchRequest(fingerprint=...)"


class PexSearchMatch(object):
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
        asset = PexSearchAsset.from_json(j["Asset"])
        segments = [Segment.from_json(s) for s in j["Segments"]]
        return PexSearchMatch(asset, segments)

    def __repr__(self):
        return "PexSearchMatch(asset={},segments={})".format(
            self.asset, self.segments
        )


class PexSearchResult(object):
    """
    This object is returned from :meth:`PexSearchFuture.get` upon
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
        A list of :class:`PexSearchMatch`.

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
            matches = [PexSearchMatch.from_json(s) for s in j["Matches"]]
        return PexSearchResult(lookup_id, matches)

    def __repr__(self):
        return "PexSearchResult(lookup_id={},matches=<{} objects>)".format(
            self.lookup_id, len(self.matches)
        )


class PexSearchFuture(object):
    """
    This object is returned by the :meth:`PexSearch.start` method
    and is used to retrieve a search result.
    """

    def __init__(self, client, lookup_id):
        self._raw_c_client = client.get()
        self._lookup_id = lookup_id

    def get(self):
        """
        Blocks until the search result is ready and then returns it.

        :raise: :class:`AEError` if the search couldn't be performed, e.g.
                because of network issues.
        :rtype: PexSearchResult
        """

        lock = _AE_Lock.new(_lib)

        c_status = _AE_Status.new(_lib)
        c_req = _AE_CheckSearchRequest.new(_lib)
        c_res = _AE_CheckSearchResult.new(_lib)

        _lib.AE_CheckSearchRequest_SetLookupID(
            c_req.get(), self._lookup_id.encode(), c_status.get()
        )
        AEError.check_status(c_status)

        _lib.AE_CheckSearch(
            self._raw_c_client, c_req.get(), c_res.get(), c_status.get()
        )
        AEError.check_status(c_status)

        c_match = _AE_SearchMatch.new(_lib)
        c_matches_pos = ctypes.c_int(0)

        c_asset = _AE_Asset.new(_lib)

        matches = []
        while _lib.AE_CheckSearchResult_NextMatch(
            c_res.get(), c_match.get(), ctypes.byref(c_matches_pos)
        ):
            _lib.AE_SearchMatch_GetAsset(c_match.get(), c_asset.get(), c_status.get())
            AEError.check_status(c_status)

            matches.append(
                PexSearchMatch(
                    asset=PexSearchAsset.extract(c_asset),
                    segments=_extract_search_segments(c_match),
                )
            )

        return PexSearchResult(
            lookup_id=self._lookup_id,
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
        return "PexSearchFuture(lookup_id={})".format(self._lookup_id)


class PexSearchClient(_Fingerprinter):
    def __init__(self, client_id, client_secret):
        self._c_client = _init_client(_ClientType.PEX_SEARCH, client_id, client_secret)

    def start_search(self, req):
        """
        Starts a Pex search. This operation does not block until the
        search is finished, it does however perform a network operation to
        initiate the search on the backend service.

        :param PexSearchRequest req: search parameters.
        :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
                because of network issues.
        :rtype: PexSearchFuture
        """

        lock = _AE_Lock.new(_lib)

        c_status = _AE_Status.new(_lib)
        c_ft = _AE_Buffer.new(_lib)
        c_req = _AE_StartSearchRequest.new(_lib)
        c_res = _AE_StartSearchResult.new(_lib)

        _lib.AE_Buffer_Set(c_ft.get(), req.fingerprint._ft, len(req.fingerprint._ft))

        _lib.AE_StartSearchRequest_SetFingerprint(
            c_req.get(), c_ft.get(), c_status.get()
        )
        AEError.check_status(c_status)

        _lib.AE_StartSearch(
            self._c_client.get(), c_req.get(), c_res.get(), c_status.get()
        )
        AEError.check_status(c_status)

        lookup_id = _lib.AE_StartSearchResult_GetLookupID(c_res.get()).decode()
        return PexSearchFuture(self._c_client, lookup_id)


def _extract_search_segments(c_match):
    c_query_start = ctypes.c_int64(0)
    c_query_end = ctypes.c_int64(0)
    c_asset_start = ctypes.c_int64(0)
    c_asset_end = ctypes.c_int64(0)
    c_type = ctypes.c_int(0)
    c_segments_pos = ctypes.c_int(0)

    segments = []
    while _lib.AE_SearchMatch_NextSegment(
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
