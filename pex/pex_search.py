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
    _Pex_Asset,
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
            isrc=_lib.Pex_Asset_GetISRC(c_asset.get()).decode(),
            label=_lib.Pex_Asset_GetLabel(c_asset.get()).decode(),
            title=_lib.Pex_Asset_GetTitle(c_asset.get()).decode(),
            artist=_lib.Pex_Asset_GetArtist(c_asset.get()).decode(),
            duration=_lib.Pex_Asset_GetDuration(c_asset.get()),
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
        A list of :class:`PexSearchMatch`.

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
        lookup_ids = j["LookupIDs"]
        matches = []
        if j.get("Matches") is not None:
            matches = [PexSearchMatch.from_json(s) for s in j["Matches"]]
        return PexSearchResult(lookup_ids, matches)

    def __repr__(self):
        return "PexSearchResult(lookup_ids={},matches=<{} objects>)".format(
            self.lookup_ids, len(self.matches)
        )


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
        :rtype: PexSearchResult
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

        c_asset = _Pex_Asset.new(_lib)

        matches = []
        while _lib.Pex_CheckSearchResult_NextMatch(
            c_res.get(), c_match.get(), ctypes.byref(c_matches_pos)
        ):
            _lib.Pex_SearchMatch_GetAsset(c_match.get(), c_asset.get(), c_status.get())
            Error.check_status(c_status)

            matches.append(
                PexSearchMatch(
                    asset=PexSearchAsset.extract(c_asset),
                    segments=_extract_segments(c_match),
                )
            )

        return PexSearchResult(
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
        return "PexSearchFuture(lookup_ids={})".format(self._lookup_ids)


class PexSearchClient(_Fingerprinter):
    def __init__(self, client_id, client_secret):
        self._c_client = _init_client(_ClientType.PEX_SEARCH, client_id, client_secret)

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

        return PexSearchFuture(self._c_client, lookup_ids)
