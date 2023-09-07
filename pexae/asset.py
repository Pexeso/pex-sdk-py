# Copyright 2020 Pexeso Inc. All rights reserved.

import ctypes

from pexae.lib import _lib


class Asset(object):
    """
    This class represents an asset and the data associated with it.
    """

    def __init__(self, id_, type_, title, artist):
        self._id = id_
        self._type = type_
        self._title = title
        self._artist = artist

    @property
    def id(self):
        """
        The ID of the asset.

        :type: str
        """
        return self._id

    @property
    def type(self):
        """
        The type of the asset.

        :type: str
        """
        return self._type

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

    def to_json(self):
        return {
            "ID": self._id,
            "Type": self._type,
            "Title": self._title,
            "Artist": self._artist,
        }

    @classmethod
    def from_json(cls, j):
        asset_id = j["ID"]
        asset_type = j["Type"]
        asset_title = j["Title"]
        asset_artist = j["Artist"]
        return Asset(asset_id, asset_type, asset_title, asset_artist)

    def __repr__(self):
        return "Asset(id={},type={},title={},artist={})".format(
            self.id, self.type, self.title, self.artist
        )


def _extract_asset(c_asset):
    return Asset(
        id_=_lib.AE_Asset_GetID(c_asset.get()).decode(),
        type_=_lib.AE_Asset_GetTypeStr(c_asset.get()).decode(),
        title=_lib.AE_Asset_GetTitle(c_asset.get()).decode(),
        artist=_lib.AE_Asset_GetArtist(c_asset.get()).decode(),
    )
