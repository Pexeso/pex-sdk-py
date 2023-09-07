# Copyright 2020 Pexeso Inc. All rights reserved.

from enum import IntEnum


class SegmentType(IntEnum):
    UNSPECIFIED = 0
    AUDIO = 1
    VIDEO = 2
    MELODY = 3


class Segment(object):
    """
    Segment is the range [start, end) in both the query and the asset of
    where the match was found within the asset.
    """

    def __init__(self, typ, query_start, query_end, asset_start, asset_end):
        self._type = typ
        self._query_start = query_start
        self._query_end = query_end
        self._asset_start = asset_start
        self._asset_end = asset_end

    @property
    def type(self):
        """
        Type of the matched segment (audio, video, melody).

        :type: SegmentType
        """
        return self._type

    @property
    def query_start(self):
        """
        The start of the matched range int the query in seconds (inclusive).

        :type: int
        """
        return self._query_start

    @property
    def query_end(self):
        """
        The end of the matched range in the query in seconds (exclusive).

        :type: int
        """
        return self._query_end

    @property
    def asset_start(self):
        """
        The start of the matched range in the asset in seconds (inclusive).

        :type: int
        """
        return self._asset_start

    @property
    def asset_end(self):
        """
        The end of the matched range in the asset in seconds (exclusive).

        :type: int
        """
        return self._asset_end

    def to_json(self):
        return {
            "Type": self._type,
            "QueryStart": self._query_start,
            "QueryEnd": self._query_end,
            "AssetStart": self._asset_start,
            "AssetEnd": self._asset_end,
        }

    @classmethod
    def from_json(cls, j):
        segment_type = SegmentType(j["Type"])
        query_start = j["QueryStart"]
        query_end = j["QueryEnd"]
        asset_start = j["AssetStart"]
        asset_end = j["AssetEnd"]
        return Segment(segment_type, query_start, query_end, asset_start, asset_end)

    def __repr__(self):
        return "Segment(type={},query_start={},query_end={},asset_start={},asset_end={})".format(
            self._type,
            self.query_start,
            self.query_end,
            self.asset_start,
            self.asset_end,
        )
