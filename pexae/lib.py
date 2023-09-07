# Copyright 2020 Pexeso Inc. All rights reserved.

import os
import ctypes
import ctypes.util
import os


MAJOR_VERSION = 3
MINOR_VERSION = 4


class _SafeObject(object):
    def __init__(self, new, delete, args=[]):
        self._obj = new(*args)
        if not self._obj:
            raise MemoryError("out of memory")
        self._delete = delete

    def __del__(self):
        self._delete(ctypes.byref(self._obj))

    def get(self):
        return self._obj


class _AE_Lock(object):
    @staticmethod
    def new(lib):
        return _AE_Lock(lib)

    def __init__(self, lib):
        self._lib = lib
        self._lib.AE_Lock()

    def __del__(self):
        self._lib.AE_Unlock()


class _AE_Status(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.AE_Status_New, lib.AE_Status_Delete)


class _AE_Buffer(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.AE_Buffer_New, lib.AE_Buffer_Delete)


class _AE_Client(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.AE_Client_New, _AE_Client.delete)

    @staticmethod
    def delete(obj):
        lock = _AE_Lock.new(_lib)
        _lib.AE_Client_Delete(obj)
        del lock
        _lib.AE_Cleanup()


class _AE_StartSearchRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_StartSearchRequest_New,
            lib.AE_StartSearchRequest_Delete,
        )


class _AE_StartSearchResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_StartSearchResult_New,
            lib.AE_StartSearchResult_Delete
        )


class _AE_CheckSearchRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_CheckSearchRequest_New,
            lib.AE_CheckSearchRequest_Delete,
        )


class _AE_CheckSearchResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_CheckSearchResult_New,
            lib.AE_CheckSearchResult_Delete
        )


class _AE_SearchMatch(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_SearchMatch_New,
            lib.AE_SearchMatch_Delete
        )


class _AE_LicenseSearchStartRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_LicenseSearchStartRequest_New,
            lib.AE_LicenseSearchStartRequest_Delete,
        )


class _AE_LicenseSearchStartResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_LicenseSearchStartResult_New, lib.AE_LicenseSearchStartResult_Delete
        )


class _AE_LicenseSearchCheckRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_LicenseSearchCheckRequest_New,
            lib.AE_LicenseSearchCheckRequest_Delete,
        )


class _AE_LicenseSearchMatch(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_LicenseSearchMatch_New, lib.AE_LicenseSearchMatch_Delete
        )


class _AE_RightsholderPolicies(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_RightsholderPolicies_New, lib.AE_RightsholderPolicies_Delete
        )


class _AE_RightsholderPolicy(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_RightsholderPolicy_New, lib.AE_RightsholderPolicy_Delete
        )


class _AE_LicenseSearchCheckResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_LicenseSearchCheckResult_New, lib.AE_LicenseSearchCheckResult_Delete
        )


class _AE_MetadataSearchStartRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_MetadataSearchStartRequest_New,
            lib.AE_MetadataSearchStartRequest_Delete,
        )


class _AE_MetadataSearchStartResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_MetadataSearchStartResult_New,
            lib.AE_MetadataSearchStartResult_Delete,
        )


class _AE_MetadataSearchCheckRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_MetadataSearchCheckRequest_New,
            lib.AE_MetadataSearchCheckRequest_Delete,
        )


class _AE_MetadataSearchCheckResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_MetadataSearchCheckResult_New,
            lib.AE_MetadataSearchCheckResult_Delete,
        )


class _AE_MetadataSearchMatch(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_MetadataSearchMatch_New, lib.AE_MetadataSearchMatch_Delete
        )


class _AE_PrivateSearchStartRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_PrivateSearchStartRequest_New,
            lib.AE_PrivateSearchStartRequest_Delete,
        )


class _AE_PrivateSearchStartResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_PrivateSearchStartResult_New,
            lib.AE_PrivateSearchStartResult_Delete,
        )


class _AE_PrivateSearchCheckRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_PrivateSearchCheckRequest_New,
            lib.AE_PrivateSearchCheckRequest_Delete,
        )


class _AE_PrivateSearchCheckResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_PrivateSearchCheckResult_New,
            lib.AE_PrivateSearchCheckResult_Delete,
        )


class _AE_PrivateSearchMatch(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.AE_PrivateSearchMatch_New, lib.AE_PrivateSearchMatch_Delete
        )


class _AE_Asset(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.AE_Asset_New, lib.AE_Asset_Delete)


def _load_lib():
    if os.getenv("PEXAE_NO_CORE_LIB") is not None:
        # Defining PEXAE_NO_CORE_LIB makes this wrapper module import-able even without the shared library.
        # Useful for generating documentation.
        return ctypes.CDLL(None)

    name = ctypes.util.find_library("pexae")
    if name is None:
        raise RuntimeError("failed to find native library")

    try:
        lib = ctypes.CDLL(name)
    except Exception:
        raise RuntimeError("failed to load native library")

    # AE_Version
    lib.AE_Version_IsCompatible.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.AE_Version_IsCompatible.restype = ctypes.c_bool

    if not lib.AE_Version_IsCompatible(MAJOR_VERSION, MINOR_VERSION):
        raise RuntimeError("bindings not compatible with native library")

    # AE_Init
    lib.AE_Init.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.AE_Init.restype = None

    lib.AE_Cleanup.argtypes = []
    lib.AE_Cleanup.restype = None

    # AE_Lock
    lib.AE_Lock.argtypes = []
    lib.AE_Lock.restype = None

    lib.AE_Unlock.argtypes = []
    lib.AE_Unlock.restype = None

    # AE_Status
    lib.AE_Status_New.argtypes = []
    lib.AE_Status_New.restype = ctypes.POINTER(_AE_Status)

    lib.AE_Status_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_AE_Status))]
    lib.AE_Status_Delete.restype = None

    lib.AE_Status_OK.argtypes = [ctypes.POINTER(_AE_Status)]
    lib.AE_Status_OK.restype = ctypes.c_bool

    lib.AE_Status_GetCode.argtypes = [ctypes.POINTER(_AE_Status)]
    lib.AE_Status_GetCode.restype = ctypes.c_int

    lib.AE_Status_GetMessage.argtypes = [ctypes.POINTER(_AE_Status)]
    lib.AE_Status_GetMessage.restype = ctypes.c_char_p

    # AE_Buffer
    lib.AE_Buffer_New.argtypes = []
    lib.AE_Buffer_New.restype = ctypes.POINTER(_AE_Buffer)

    lib.AE_Buffer_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_AE_Buffer))]
    lib.AE_Buffer_Delete.restype = None

    lib.AE_Buffer_Set.argtypes = [
        ctypes.POINTER(_AE_Buffer),
        ctypes.c_void_p,
        ctypes.c_size_t,
    ]
    lib.AE_Buffer_Set.restype = None

    lib.AE_Buffer_GetData.argtypes = [ctypes.POINTER(_AE_Buffer)]
    lib.AE_Buffer_GetData.restype = ctypes.c_void_p

    lib.AE_Buffer_GetSize.argtypes = [ctypes.POINTER(_AE_Buffer)]
    lib.AE_Buffer_GetSize.restype = ctypes.c_size_t

    # AE_Fingerprint
    lib.AE_Fingerprint_File_For_Types.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
        ctypes.c_int,
    ]
    lib.AE_Fingerprint_File_For_Types.restype = None

    lib.AE_Fingerprint_Buffer_For_Types.argtypes = [
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
        ctypes.c_int,
    ]
    lib.AE_Fingerprint_Buffer_For_Types.restype = None

    # AE_Client
    lib.AE_Client_New.argtypes = []
    lib.AE_Client_New.restype = ctypes.POINTER(_AE_Client)

    lib.AE_Client_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_AE_Client))]
    lib.AE_Client_Delete.restype = None

    lib.AE_Client_Init.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_Client_Init.restype = None

    lib.AE_Client_InitType.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_Client_InitType.restype = None

    # AE_Mockserver
    lib.AE_Mockserver_InitClient.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_Mockserver_InitClient.restype = None

    # AE_LicenseSearch
    lib.AE_LicenseSearch_Start.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_LicenseSearchStartRequest),
        ctypes.POINTER(_AE_LicenseSearchStartResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_LicenseSearch_Start.restype = None

    lib.AE_LicenseSearch_Check.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_LicenseSearchCheckRequest),
        ctypes.POINTER(_AE_LicenseSearchCheckResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_LicenseSearch_Check.restype = None

    # AE_LicenseSearchStartRequest
    lib.AE_LicenseSearchStartRequest_New.argtypes = []
    lib.AE_LicenseSearchStartRequest_New.restype = ctypes.POINTER(
        _AE_LicenseSearchStartRequest
    )

    lib.AE_LicenseSearchStartRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_LicenseSearchStartRequest))
    ]
    lib.AE_LicenseSearchStartRequest_Delete.restype = None

    lib.AE_LicenseSearchStartRequest_SetFingerprint.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchStartRequest),
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_LicenseSearchStartRequest_SetFingerprint.restype = None

    # AE_LicenseSearchStartResult
    lib.AE_LicenseSearchStartResult_New.argtypes = []
    lib.AE_LicenseSearchStartResult_New.restype = ctypes.POINTER(
        _AE_LicenseSearchStartResult
    )

    lib.AE_LicenseSearchStartResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_LicenseSearchStartResult))
    ]
    lib.AE_LicenseSearchStartResult_Delete.restype = None

    lib.AE_LicenseSearchStartResult_GetLookupID.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchStartResult)
    ]
    lib.AE_LicenseSearchStartResult_GetLookupID.restype = ctypes.c_char_p

    lib.AE_LicenseSearchStartResult_GetUGCID.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchStartResult)
    ]
    lib.AE_LicenseSearchStartResult_GetUGCID.restype = ctypes.c_char_p

    # AE_LicenseSearchCheckRequest
    lib.AE_LicenseSearchCheckRequest_New.argtypes = []
    lib.AE_LicenseSearchCheckRequest_New.restype = ctypes.POINTER(
        _AE_LicenseSearchCheckRequest
    )

    lib.AE_LicenseSearchCheckRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_LicenseSearchCheckRequest))
    ]
    lib.AE_LicenseSearchCheckRequest_Delete.restype = None

    lib.AE_LicenseSearchCheckRequest_SetLookupID.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchCheckRequest),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_LicenseSearchCheckRequest_SetLookupID.restype = None

    # AE_LicenseSearchCheckResult
    lib.AE_LicenseSearchCheckResult_New.argtypes = []
    lib.AE_LicenseSearchCheckResult_New.restype = ctypes.POINTER(
        _AE_LicenseSearchCheckResult
    )

    lib.AE_LicenseSearchCheckResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_LicenseSearchCheckResult))
    ]
    lib.AE_LicenseSearchCheckResult_Delete.restype = None

    lib.AE_LicenseSearchCheckResult_GetLookupID.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchCheckResult)
    ]
    lib.AE_LicenseSearchCheckResult_GetLookupID.restype = ctypes.c_char_p

    lib.AE_LicenseSearchCheckResult_GetUGCID.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchCheckResult)
    ]
    lib.AE_LicenseSearchCheckResult_GetUGCID.restype = ctypes.c_char_p

    lib.AE_LicenseSearchCheckResult_NextMatch.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchCheckResult),
        ctypes.POINTER(_AE_LicenseSearchMatch),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_LicenseSearchCheckResult_NextMatch.restype = ctypes.c_bool

    # AE_LicenseSearchMatch
    lib.AE_LicenseSearchMatch_New.argtypes = []
    lib.AE_LicenseSearchMatch_New.restype = ctypes.POINTER(_AE_LicenseSearchMatch)

    lib.AE_LicenseSearchMatch_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_LicenseSearchMatch))
    ]
    lib.AE_LicenseSearchMatch_Delete.restype = None

    lib.AE_LicenseSearchMatch_GetAsset.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchMatch),
        ctypes.POINTER(_AE_Asset),
    ]
    lib.AE_LicenseSearchMatch_GetAsset.restype = None

    lib.AE_LicenseSearchMatch_NextSegment.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchMatch),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_LicenseSearchMatch_NextSegment.restype = ctypes.c_bool

    lib.AE_LicenseSearchMatch_NextTerritoryPolicies.argtypes = [
        ctypes.POINTER(_AE_LicenseSearchMatch),
        ctypes.POINTER(ctypes.c_char_p),
        ctypes.POINTER(_AE_RightsholderPolicies),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_LicenseSearchMatch_NextTerritoryPolicies.restype = ctypes.c_bool

    # AE_RightsholderPolicies
    lib.AE_RightsholderPolicies_New.argtypes = []
    lib.AE_RightsholderPolicies_New.restype = ctypes.POINTER(_AE_RightsholderPolicies)

    lib.AE_RightsholderPolicies_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_RightsholderPolicies))
    ]
    lib.AE_RightsholderPolicies_Delete.restype = None

    lib.AE_RightsholderPolicies_Next.argtypes = [
        ctypes.POINTER(_AE_RightsholderPolicies),
        ctypes.POINTER(_AE_RightsholderPolicy),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_RightsholderPolicies_Next.restype = ctypes.c_bool

    # AE_RightsholderPolicy
    lib.AE_RightsholderPolicy_New.argtypes = []
    lib.AE_RightsholderPolicy_New.restype = ctypes.POINTER(_AE_RightsholderPolicy)

    lib.AE_RightsholderPolicy_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_RightsholderPolicy))
    ]
    lib.AE_RightsholderPolicy_Delete.restype = None

    lib.AE_RightsholderPolicy_GetRightsholderID.argtypes = [
        ctypes.POINTER(_AE_RightsholderPolicy)
    ]
    lib.AE_RightsholderPolicy_GetRightsholderID.restype = ctypes.c_char_p

    lib.AE_RightsholderPolicy_GetRightsholderTitle.argtypes = [
        ctypes.POINTER(_AE_RightsholderPolicy)
    ]
    lib.AE_RightsholderPolicy_GetRightsholderTitle.restype = ctypes.c_char_p

    lib.AE_RightsholderPolicy_GetPolicyID.argtypes = [
        ctypes.POINTER(_AE_RightsholderPolicy)
    ]
    lib.AE_RightsholderPolicy_GetPolicyID.restype = ctypes.c_char_p

    lib.AE_RightsholderPolicy_GetPolicyCategoryID.argtypes = [
        ctypes.POINTER(_AE_RightsholderPolicy)
    ]
    lib.AE_RightsholderPolicy_GetPolicyCategoryID.restype = ctypes.c_char_p

    lib.AE_RightsholderPolicy_GetPolicyCategoryName.argtypes = [
        ctypes.POINTER(_AE_RightsholderPolicy)
    ]
    lib.AE_RightsholderPolicy_GetPolicyCategoryName.restype = ctypes.c_char_p

    # AE_StartSearch
    lib.AE_StartSearch.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_StartSearchRequest),
        ctypes.POINTER(_AE_StartSearchResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_StartSearch.restype = None

    # AE_CheckSearch
    lib.AE_CheckSearch.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_CheckSearchRequest),
        ctypes.POINTER(_AE_CheckSearchResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_CheckSearch.restype = None

    # AE_StartSearchRequest
    lib.AE_StartSearchRequest_New.argtypes = []
    lib.AE_StartSearchRequest_New.restype = ctypes.POINTER(
        _AE_StartSearchRequest
    )

    lib.AE_StartSearchRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_StartSearchRequest))
    ]
    lib.AE_StartSearchRequest_Delete.restype = None

    lib.AE_StartSearchRequest_SetFingerprint.argtypes = [
        ctypes.POINTER(_AE_StartSearchRequest),
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_StartSearchRequest_SetFingerprint.restype = None

    # AE_StartSearchResult
    lib.AE_StartSearchResult_New.argtypes = []
    lib.AE_StartSearchResult_New.restype = ctypes.POINTER(
        _AE_StartSearchResult
    )

    lib.AE_StartSearchResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_StartSearchResult))
    ]
    lib.AE_StartSearchResult_Delete.restype = None

    lib.AE_StartSearchResult_GetLookupID.argtypes = [
        ctypes.POINTER(_AE_StartSearchResult)
    ]
    lib.AE_StartSearchResult_GetLookupID.restype = ctypes.c_char_p

    # AE_CheckSearchRequest
    lib.AE_CheckSearchRequest_New.argtypes = []
    lib.AE_CheckSearchRequest_New.restype = ctypes.POINTER(
        _AE_CheckSearchRequest
    )

    lib.AE_CheckSearchRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_CheckSearchRequest))
    ]
    lib.AE_CheckSearchRequest_Delete.restype = None

    lib.AE_CheckSearchRequest_SetLookupID.argtypes = [
        ctypes.POINTER(_AE_CheckSearchRequest),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_CheckSearchRequest_SetLookupID.restype = None

    # AE_CheckSearchResult
    lib.AE_CheckSearchResult_New.argtypes = []
    lib.AE_CheckSearchResult_New.restype = ctypes.POINTER(
        _AE_CheckSearchResult
    )

    lib.AE_CheckSearchResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_CheckSearchResult))
    ]
    lib.AE_CheckSearchResult_Delete.restype = None

    lib.AE_CheckSearchResult_NextMatch.argtypes = [
        ctypes.POINTER(_AE_CheckSearchResult),
        ctypes.POINTER(_AE_SearchMatch),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_CheckSearchResult_NextMatch.restype = ctypes.c_bool

    # AE_SearchMatch
    lib.AE_SearchMatch_New.argtypes = []
    lib.AE_SearchMatch_New.restype = ctypes.POINTER(_AE_SearchMatch)

    lib.AE_SearchMatch_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_SearchMatch))
    ]
    lib.AE_SearchMatch_Delete.restype = None

    lib.AE_SearchMatch_GetAsset.argtypes = [
        ctypes.POINTER(_AE_SearchMatch),
        ctypes.POINTER(_AE_Asset),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_SearchMatch_GetAsset.restype = None

    lib.AE_SearchMatch_NextSegment.argtypes = [
        ctypes.POINTER(_AE_SearchMatch),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_SearchMatch_NextSegment.restype = ctypes.c_bool


    # AE_MetadataSearch
    lib.AE_MetadataSearch_Start.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_MetadataSearchStartRequest),
        ctypes.POINTER(_AE_MetadataSearchStartResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_MetadataSearch_Start.restype = None

    lib.AE_MetadataSearch_Check.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_MetadataSearchCheckRequest),
        ctypes.POINTER(_AE_MetadataSearchCheckResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_MetadataSearch_Check.restype = None

    # AE_MetadataSearchStartRequest
    lib.AE_MetadataSearchStartRequest_New.argtypes = []
    lib.AE_MetadataSearchStartRequest_New.restype = ctypes.POINTER(
        _AE_MetadataSearchStartRequest
    )

    lib.AE_MetadataSearchStartRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_MetadataSearchStartRequest))
    ]
    lib.AE_MetadataSearchStartRequest_Delete.restype = None

    lib.AE_MetadataSearchStartRequest_SetFingerprint.argtypes = [
        ctypes.POINTER(_AE_MetadataSearchStartRequest),
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_MetadataSearchStartRequest_SetFingerprint.restype = None

    # AE_MetadataSearchStartResult
    lib.AE_MetadataSearchStartResult_New.argtypes = []
    lib.AE_MetadataSearchStartResult_New.restype = ctypes.POINTER(
        _AE_MetadataSearchStartResult
    )

    lib.AE_MetadataSearchStartResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_MetadataSearchStartResult))
    ]
    lib.AE_MetadataSearchStartResult_Delete.restype = None

    lib.AE_MetadataSearchStartResult_GetLookupID.argtypes = [
        ctypes.POINTER(_AE_MetadataSearchStartResult)
    ]
    lib.AE_MetadataSearchStartResult_GetLookupID.restype = ctypes.c_char_p

    # AE_MetadataSearchCheckRequest
    lib.AE_MetadataSearchCheckRequest_New.argtypes = []
    lib.AE_MetadataSearchCheckRequest_New.restype = ctypes.POINTER(
        _AE_MetadataSearchCheckRequest
    )

    lib.AE_MetadataSearchCheckRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_MetadataSearchCheckRequest))
    ]
    lib.AE_MetadataSearchCheckRequest_Delete.restype = None

    lib.AE_MetadataSearchCheckRequest_SetLookupID.argtypes = [
        ctypes.POINTER(_AE_MetadataSearchCheckRequest),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_MetadataSearchCheckRequest_SetLookupID.restype = None

    # AE_MetadataSearchCheckResult
    lib.AE_MetadataSearchCheckResult_New.argtypes = []
    lib.AE_MetadataSearchCheckResult_New.restype = ctypes.POINTER(
        _AE_MetadataSearchCheckResult
    )

    lib.AE_MetadataSearchCheckResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_MetadataSearchCheckResult))
    ]
    lib.AE_MetadataSearchCheckResult_Delete.restype = None

    lib.AE_MetadataSearchCheckResult_GetLookupID.argtypes = [
        ctypes.POINTER(_AE_MetadataSearchCheckResult)
    ]
    lib.AE_MetadataSearchCheckResult_GetLookupID.restype = ctypes.c_char_p

    lib.AE_MetadataSearchCheckResult_NextMatch.argtypes = [
        ctypes.POINTER(_AE_MetadataSearchCheckResult),
        ctypes.POINTER(_AE_MetadataSearchMatch),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_MetadataSearchCheckResult_NextMatch.restype = ctypes.c_bool

    # AE_MetadataSearchMatch
    lib.AE_MetadataSearchMatch_New.argtypes = []
    lib.AE_MetadataSearchMatch_New.restype = ctypes.POINTER(_AE_MetadataSearchMatch)

    lib.AE_MetadataSearchMatch_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_MetadataSearchMatch))
    ]
    lib.AE_MetadataSearchMatch_Delete.restype = None

    lib.AE_MetadataSearchMatch_GetAsset.argtypes = [
        ctypes.POINTER(_AE_MetadataSearchMatch),
        ctypes.POINTER(_AE_Asset),
    ]
    lib.AE_MetadataSearchMatch_GetAsset.restype = None

    lib.AE_MetadataSearchMatch_NextSegment.argtypes = [
        ctypes.POINTER(_AE_MetadataSearchMatch),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_MetadataSearchMatch_NextSegment.restype = ctypes.c_bool

    # AE_PrivateSearch_Ingest
    lib.AE_PrivateSearch_Ingest.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_PrivateSearch_Ingest.restype = None

    # AE_PrivateSearch
    lib.AE_PrivateSearch_Start.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_PrivateSearchStartRequest),
        ctypes.POINTER(_AE_PrivateSearchStartResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_PrivateSearch_Start.restype = None

    lib.AE_PrivateSearch_Check.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.POINTER(_AE_PrivateSearchCheckRequest),
        ctypes.POINTER(_AE_PrivateSearchCheckResult),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_PrivateSearch_Check.restype = None

    # AE_PrivateSearchStartRequest
    lib.AE_PrivateSearchStartRequest_New.argtypes = []
    lib.AE_PrivateSearchStartRequest_New.restype = ctypes.POINTER(
        _AE_PrivateSearchStartRequest
    )

    lib.AE_PrivateSearchStartRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_PrivateSearchStartRequest))
    ]
    lib.AE_PrivateSearchStartRequest_Delete.restype = None

    lib.AE_PrivateSearchStartRequest_SetFingerprint.argtypes = [
        ctypes.POINTER(_AE_PrivateSearchStartRequest),
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_PrivateSearchStartRequest_SetFingerprint.restype = None

    # AE_PrivateSearchStartResult
    lib.AE_PrivateSearchStartResult_New.argtypes = []
    lib.AE_PrivateSearchStartResult_New.restype = ctypes.POINTER(
        _AE_PrivateSearchStartResult
    )

    lib.AE_PrivateSearchStartResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_PrivateSearchStartResult))
    ]
    lib.AE_PrivateSearchStartResult_Delete.restype = None

    lib.AE_PrivateSearchStartResult_GetLookupID.argtypes = [
        ctypes.POINTER(_AE_PrivateSearchStartResult)
    ]
    lib.AE_PrivateSearchStartResult_GetLookupID.restype = ctypes.c_char_p

    # AE_PrivateSearchCheckRequest
    lib.AE_PrivateSearchCheckRequest_New.argtypes = []
    lib.AE_PrivateSearchCheckRequest_New.restype = ctypes.POINTER(
        _AE_PrivateSearchCheckRequest
    )

    lib.AE_PrivateSearchCheckRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_PrivateSearchCheckRequest))
    ]
    lib.AE_PrivateSearchCheckRequest_Delete.restype = None

    lib.AE_PrivateSearchCheckRequest_SetLookupID.argtypes = [
        ctypes.POINTER(_AE_PrivateSearchCheckRequest),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_PrivateSearchCheckRequest_SetLookupID.restype = None

    # AE_PrivateSearchCheckResult
    lib.AE_PrivateSearchCheckResult_New.argtypes = []
    lib.AE_PrivateSearchCheckResult_New.restype = ctypes.POINTER(
        _AE_PrivateSearchCheckResult
    )

    lib.AE_PrivateSearchCheckResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_PrivateSearchCheckResult))
    ]
    lib.AE_PrivateSearchCheckResult_Delete.restype = None

    lib.AE_PrivateSearchCheckResult_GetLookupID.argtypes = [
        ctypes.POINTER(_AE_PrivateSearchCheckResult)
    ]
    lib.AE_PrivateSearchCheckResult_GetLookupID.restype = ctypes.c_char_p

    lib.AE_PrivateSearchCheckResult_NextMatch.argtypes = [
        ctypes.POINTER(_AE_PrivateSearchCheckResult),
        ctypes.POINTER(_AE_PrivateSearchMatch),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_PrivateSearchCheckResult_NextMatch.restype = ctypes.c_bool

    # AE_PrivateSearchMatch
    lib.AE_PrivateSearchMatch_New.argtypes = []
    lib.AE_PrivateSearchMatch_New.restype = ctypes.POINTER(_AE_PrivateSearchMatch)

    lib.AE_PrivateSearchMatch_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_AE_PrivateSearchMatch))
    ]
    lib.AE_PrivateSearchMatch_Delete.restype = None

    lib.AE_PrivateSearchMatch_GetProvidedID.argtypes = [
        ctypes.POINTER(_AE_PrivateSearchMatch),
    ]
    lib.AE_PrivateSearchMatch_GetProvidedID.restype = ctypes.c_char_p

    lib.AE_PrivateSearchMatch_NextSegment.argtypes = [
        ctypes.POINTER(_AE_PrivateSearchMatch),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.AE_PrivateSearchMatch_NextSegment.restype = ctypes.c_bool

    # AE_Asset
    lib.AE_Asset_New.argtypes = []
    lib.AE_Asset_New.restype = ctypes.POINTER(_AE_Asset)

    lib.AE_Asset_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_AE_Asset))]
    lib.AE_Asset_Delete.restype = None

    lib.AE_Asset_GetID.argtypes = [ctypes.POINTER(_AE_Asset)]
    lib.AE_Asset_GetID.restype = ctypes.c_char_p

    lib.AE_Asset_GetTypeStr.argtypes = [ctypes.POINTER(_AE_Asset)]
    lib.AE_Asset_GetTypeStr.restype = ctypes.c_char_p

    lib.AE_Asset_GetISRC.argtypes = [ctypes.POINTER(_AE_Asset)]
    lib.AE_Asset_GetISRC.restype = ctypes.c_char_p

    lib.AE_Asset_GetLabel.argtypes = [ctypes.POINTER(_AE_Asset)]
    lib.AE_Asset_GetLabel.restype = ctypes.c_char_p

    lib.AE_Asset_GetTitle.argtypes = [ctypes.POINTER(_AE_Asset)]
    lib.AE_Asset_GetTitle.restype = ctypes.c_char_p

    lib.AE_Asset_GetArtist.argtypes = [ctypes.POINTER(_AE_Asset)]
    lib.AE_Asset_GetArtist.restype = ctypes.c_char_p

    lib.AE_Asset_GetDuration.argtypes = [ctypes.POINTER(_AE_Asset)]
    lib.AE_Asset_GetDuration.restype = ctypes.c_float

    return lib


_lib = _load_lib()
