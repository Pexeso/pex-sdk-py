# Copyright 2020 Pexeso Inc. All rights reserved.

import ctypes
from datetime import datetime
from collections import namedtuple

from pexae.lib import (
    _lib,
    _AE_Status,
    _AE_Lock,
    _AE_Buffer,
    _AE_Asset,
    _AE_LicenseSearchMatch,
    _AE_LicenseSearchStartRequest,
    _AE_LicenseSearchStartResult,
    _AE_LicenseSearchCheckRequest,
    _AE_LicenseSearchCheckResult,
    _AE_RightsholderPolicies,
    _AE_RightsholderPolicy,
)
from pexae.errors import AEError
from pexae.common import SegmentType, Segment
from pexae.asset import Asset, _extract_asset


class LicenseSearchRequest(object):
    """
    Holds all data necessary to perform a license search. A search can only be
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
        return "LicenseSearchRequest(fingerprint=...)"


class RightsholderPolicy(object):
    """ """

    def __init__(
        self,
        rightsholder_id,
        rightsholder_title,
        policy_id,
        policy_category_id,
        policy_category_name,
    ):
        self._rightsholder_id = rightsholder_id
        self._rightsholder_title = rightsholder_title
        self._policy_id = policy_id
        self._policy_category_id = policy_category_id
        self._policy_category_name = policy_category_name

    @property
    def rightsholder_id(self):
        """
        The ID of the rightsholder.

        :type: str
        """
        return self._rightsholder_id

    @property
    def rightsholder_title(self):
        """
        The title of the rightsholder.

        :type: str
        """
        return self._rightsholder_title

    @property
    def policy_id(self):
        """
        The ID of the policy.

        :type: str
        """
        return self._policy_id

    @property
    def policy_category_id(self):
        """
        The ID of the category this policy belongs to.

        :type: str
        """
        return self._policy_category_id

    @property
    def policy_category_name(self):
        """
        The name of the category this policy belongs to.

        :type: str
        """
        return self._policy_category_name

    def to_json(self):
        return {
            "RightsholderID": self._rightsholder_id,
            "RightsholderTitle": self._rightsholder_title,
            "PolicyID": self._policy_id,
            "PolicyCategoryID": self._policy_category_id,
            "PolicyCategoryName": self._policy_category_name,
        }

    @classmethod
    def from_json(cls, j):
        rightsholder_id = j["RightsholderID"]
        rightsholder_title = j["RightsholderTitle"]
        policy_id = j["PolicyID"]
        policy_category_id = j["PolicyCategoryID"]
        policy_category_name = j["PolicyCategoryName"]
        return RightsholderPolicy(
            rightsholder_id,
            rightsholder_title,
            policy_id,
            policy_category_id,
            policy_category_name,
        )

    def __repr__(self):
        return "RightsholderPolicy(rightsholder_id={},rightsholder_title={},policy_id={},policy_category_id={},policy_category_name={})".format(
            self.rightsholder_id,
            self.rightsholder_title,
            self.policy_id,
            self.policy_category_id,
            self.policy_category_name,
        )


class LicenseSearchMatch(object):
    """
    Contains detailed information about the match, including information about
    the matched asset, and the matching segments.
    """

    def __init__(self, asset, segments, policies):
        self._asset = asset
        self._segments = segments
        self._policies = policies

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

    @property
    def policies(self):
        """
            A map where the key is a territory and the value is
            RightsholderPolicy. The territory codes conform to the ISO 3166-1
            alpha-2 standard. For more information visit
            https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.

        :type: dict
        """
        return self._policies

    def to_json(self):
        policies = {}
        for k, v in self._policies.items():
            policies[k] = [p.to_json() for p in v]

        return {
            "Asset": self._asset.to_json(),
            "Segments": [s.to_json() for s in self._segments],
            "Policies": policies,
        }

    @classmethod
    def from_json(cls, j):
        asset = Asset.from_json(j["Asset"])
        segments = [Segment.from_json(s) for s in j["Segments"]]

        policies = {}
        for k, v in j["Policies"].items():
            policies[k] = [RightsholderPolicy.from_json(p) for p in v]

        return LicenseSearchMatch(asset, segments, policies)

    def __repr__(self):
        return "LicenseSearchMatch(asset={},segments={},policies=<{} objects>)".format(
            self.asset, self.segments, len(self.policies)
        )


class LicenseSearchResult(object):
    """
    This object is returned from :meth:`LicenseSearchFuture.get` upon
    successful comptetion.
    """

    def __init__(self, lookup_id, ugc_id, matches):
        self._lookup_id = lookup_id
        self._ugc_id = ugc_id
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
    def ugc_id(self):
        """
        An ID that uniquely identifies the UGC. It is used to provide UGC
        metadata back to Pex.

        :type: int
        """
        return self._ugc_id

    @property
    def matches(self):
        """
        A list of :class:`LicenseSearchMatch`.

        :type: list
        """
        return self._matches

    def to_json(self):
        return {
            "LookupID": self._lookup_id,
            "UGCID": self._ugc_id,
            "Matches": [m.to_json() for m in self._matches],
        }

    @classmethod
    def from_json(cls, j):
        lookup_id = j["LookupID"]
        ugc_id = j["UGCID"]
        matches = []
        if j.get("Matches") is not None:
            matches = [LicenseSearchMatch.from_json(s) for s in j["Matches"]]
        return LicenseSearchResult(lookup_id, ugc_id, matches)

    def __repr__(self):
        return "LicenseSearchResult(lookup_id={},ugc_id={},matches=<{} objects>".format(
            self.lookup_id, self.ugc_id, len(self.matches)
        )


class LicenseSearchFuture(object):
    """
    This object is returned by the :meth:`Client.start_license_search` method
    and is used to retrieve a search result.
    """

    def __init__(self, client, lookup_id, ugc_id):
        self._raw_c_client = client._c_client.get()
        self._lookup_id = lookup_id
        self._ugc_id = ugc_id

    def get(self):
        """
        Blocks until the search result is ready and then returns it.

        :raise: :class:`AEError` if the search couldn't be performed, e.g.
                because of network issues.
        :rtype: LicenseSearchResult
        """

        lock = _AE_Lock.new(_lib)

        c_status = _AE_Status.new(_lib)
        c_req = _AE_LicenseSearchCheckRequest.new(_lib)
        c_res = _AE_LicenseSearchCheckResult.new(_lib)

        _lib.AE_LicenseSearchCheckRequest_SetLookupID(
            c_req.get(), self._lookup_id.encode(), c_status.get()
        )
        AEError.check_status(c_status)

        _lib.AE_LicenseSearch_Check(
            self._raw_c_client, c_req.get(), c_res.get(), c_status.get()
        )
        AEError.check_status(c_status)

        c_match = _AE_LicenseSearchMatch.new(_lib)
        c_matches_pos = ctypes.c_int(0)

        c_asset = _AE_Asset.new(_lib)

        matches = []
        while _lib.AE_LicenseSearchCheckResult_NextMatch(
            c_res.get(), c_match.get(), ctypes.byref(c_matches_pos)
        ):
            _lib.AE_LicenseSearchMatch_GetAsset(c_match.get(), c_asset.get())

            matches.append(
                LicenseSearchMatch(
                    asset=_extract_asset(c_asset),
                    segments=_extract_license_search_segments(c_match),
                    policies=_extract_license_search_policies(c_match),
                )
            )

        return LicenseSearchResult(
            lookup_id=_lib.AE_LicenseSearchCheckResult_GetLookupID(
                c_res.get()
            ).decode(),
            ugc_id=_lib.AE_LicenseSearchCheckResult_GetUGCID(c_res.get()).decode(),
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

    @property
    def ugc_id(self):
        """
        An ID that uniquely identifies the user-generated content.
        Can be used for diagnostics.

        :type: str
        """
        return self._ugc_id

    def __repr__(self):
        return "LicenseSearchFuture(lookup_id={},ugc_id={})".format(
            self._lookup_id, self._ugc_id
        )


def _start_license_search(client, req):
    """
    Starts a license search. This operation does not block until the
    search is finished, it does however perform a network operation to
    initiate the search on the backend service.

    :param LicenseSearchRequest req: search parameters.
    :raise: :class:`AEError` if the search couldn’t be initiated, e.g.
            because of network issues.
    :rtype: LicenseSearchFuture
    """

    lock = _AE_Lock.new(_lib)

    c_status = _AE_Status.new(_lib)
    c_ft = _AE_Buffer.new(_lib)
    c_req = _AE_LicenseSearchStartRequest.new(_lib)
    c_res = _AE_LicenseSearchStartResult.new(_lib)

    _lib.AE_Buffer_Set(c_ft.get(), req.fingerprint._ft, len(req.fingerprint._ft))

    _lib.AE_LicenseSearchStartRequest_SetFingerprint(
        c_req.get(), c_ft.get(), c_status.get()
    )
    AEError.check_status(c_status)

    _lib.AE_LicenseSearch_Start(
        client._c_client.get(), c_req.get(), c_res.get(), c_status.get()
    )
    AEError.check_status(c_status)

    lookup_id = _lib.AE_LicenseSearchStartResult_GetLookupID(c_res.get()).decode()
    ugc_id = _lib.AE_LicenseSearchStartResult_GetUGCID(c_res.get()).decode()
    return LicenseSearchFuture(client, lookup_id, ugc_id)


def _extract_license_search_policies(c_match):
    c_rightsholder_policies = _AE_RightsholderPolicies.new(_lib)
    c_rightsholder_policy = _AE_RightsholderPolicy.new(_lib)

    c_territory = ctypes.c_char_p()
    c_territory_policies_pos = ctypes.c_int(0)
    territory_policies = {}

    while _lib.AE_LicenseSearchMatch_NextTerritoryPolicies(
        c_match.get(),
        ctypes.byref(c_territory),
        c_rightsholder_policies.get(),
        ctypes.byref(c_territory_policies_pos),
    ):
        c_rightsholder_policies_pos = ctypes.c_int(0)
        policies = []

        while _lib.AE_RightsholderPolicies_Next(
            c_rightsholder_policies.get(),
            c_rightsholder_policy.get(),
            ctypes.byref(c_rightsholder_policies_pos),
        ):
            policies.append(
                RightsholderPolicy(
                    rightsholder_id=_lib.AE_RightsholderPolicy_GetRightsholderID(
                        c_rightsholder_policy.get()
                    ).decode(),
                    rightsholder_title=_lib.AE_RightsholderPolicy_GetRightsholderTitle(
                        c_rightsholder_policy.get()
                    ).decode(),
                    policy_id=_lib.AE_RightsholderPolicy_GetPolicyID(
                        c_rightsholder_policy.get()
                    ).decode(),
                    policy_category_id=_lib.AE_RightsholderPolicy_GetPolicyCategoryID(
                        c_rightsholder_policy.get()
                    ).decode(),
                    policy_category_name=_lib.AE_RightsholderPolicy_GetPolicyCategoryName(
                        c_rightsholder_policy.get()
                    ).decode(),
                )
            )
        territory_policies[c_territory.value.decode()] = policies
    return territory_policies


def _extract_license_search_segments(c_match):
    c_query_start = ctypes.c_int64(0)
    c_query_end = ctypes.c_int64(0)
    c_asset_start = ctypes.c_int64(0)
    c_asset_end = ctypes.c_int64(0)
    c_type = ctypes.c_int(0)
    c_segments_pos = ctypes.c_int(0)

    segments = []
    while _lib.AE_LicenseSearchMatch_NextSegment(
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
