# Copyright 2023 Pexeso Inc. All rights reserved.

import os
import ctypes
import ctypes.util
import os


MAJOR_VERSION = 4
MINOR_VERSION = 0


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


class _AE_Asset(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.AE_Asset_New, lib.AE_Asset_Delete)


def _load_lib():
    if os.getenv("PEX_SDK_NO_CORE_LIB") is not None:
        # Defining PEX_SDK_NO_CORE_LIB makes this wrapper module import-able even without the shared library.
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
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_Client_Init.restype = None

    # AE_Mockserver
    lib.AE_Mockserver_InitClient.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_Mockserver_InitClient.restype = None

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

    lib.AE_SearchMatch_GetProvidedID.argtypes = [
        ctypes.POINTER(_AE_SearchMatch),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_SearchMatch_GetProvidedID.restype = ctypes.c_char_p

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

    # AE_Ingest
    lib.AE_Ingest.argtypes = [
        ctypes.POINTER(_AE_Client),
        ctypes.c_char_p,
        ctypes.POINTER(_AE_Buffer),
        ctypes.POINTER(_AE_Status),
    ]
    lib.AE_Ingest.restype = None

    # AE_Asset
    lib.AE_Asset_New.argtypes = []
    lib.AE_Asset_New.restype = ctypes.POINTER(_AE_Asset)

    lib.AE_Asset_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_AE_Asset))]
    lib.AE_Asset_Delete.restype = None

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
