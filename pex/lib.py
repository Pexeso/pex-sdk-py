# Copyright 2023 Pexeso Inc. All rights reserved.

import ctypes
import ctypes.util
import os

MAJOR_VERSION = 4
MINOR_VERSION = 5


class _SafeObject(object):
    def __init__(self, new, delete, args=None):
        self._new = new
        self._delete = delete
        self._args = args
        self._obj = None

    def __del__(self):
        self.free()

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.free()

    def init(self):
        args = []
        if self._args is not None:
            args = self._args
        self._obj = self._new(*args)
        if not self._obj:
            raise MemoryError("out of memory")

    def free(self):
        if not self._obj:
            return
        self._delete(ctypes.byref(self._obj))
        self._obj = None

    def get(self):
        if not self._obj:
            raise RuntimeError("use object in a with statement")
        return self._obj


class _Pex_Lock(object):
    @staticmethod
    def new(lib):
        return _Pex_Lock(lib)

    def __init__(self, lib):
        self._lib = lib

    def __enter__(self):
        self._lib.Pex_Lock()

    def __exit__(self, exc_type, exc_value, traceback):
        self._lib.Pex_Unlock()


class _Pex_Status(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.Pex_Status_New, lib.Pex_Status_Delete)


class _Pex_Buffer(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.Pex_Buffer_New, lib.Pex_Buffer_Delete)


class _Pex_Client(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(lib.Pex_Client_New, _Pex_Client.delete)

    @staticmethod
    def delete(obj):
        lock = _Pex_Lock.new(_lib)
        _lib.Pex_Client_Delete(obj)
        del lock
        _lib.Pex_Cleanup()


class _Pex_StartSearchRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.Pex_StartSearchRequest_New,
            lib.Pex_StartSearchRequest_Delete,
        )


class _Pex_StartSearchResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.Pex_StartSearchResult_New,
            lib.Pex_StartSearchResult_Delete
        )


class _Pex_CheckSearchRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.Pex_CheckSearchRequest_New,
            lib.Pex_CheckSearchRequest_Delete,
        )


class _Pex_CheckSearchResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.Pex_CheckSearchResult_New,
            lib.Pex_CheckSearchResult_Delete
        )


class _Pex_ListRequest(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.Pex_ListRequest_New,
            lib.Pex_ListRequest_Delete,
        )


class _Pex_ListResult(ctypes.Structure):
    @staticmethod
    def new(lib):
        return _SafeObject(
            lib.Pex_ListResult_New,
            lib.Pex_ListResult_Delete
        )


def _load_lib():
    if os.getenv("PEX_SDK_NO_CORE_LIB") is not None:
        # Defining PEX_SDK_NO_CORE_LIB makes this wrapper module import-able even without the shared library.
        # Useful for generating documentation.
        return ctypes.CDLL(None)

    # `find_library` is rather impractical on Windows for two reasons
    # 1) it does not search the same paths that Windows's dynamic linking does
    # 2) Windows does not have a good central location for installing DLLs like
    #    linux does. (This is advantageous in preventing dll hell, but
    #    causes issues with testing non-packaged builds).
    # Thus we allow it to be overridden through env var (on all platforms).
    if 'PEX_SDK_UPDATER_LIB' in os.environ:
        name = os.environ['PEX_SDK_UPDATER_LIB']
    else:
        name = ctypes.util.find_library("pexsdk")

    if name is None:
        raise RuntimeError("failed to find native library")

    try:
        lib = ctypes.CDLL(name)
    except Exception:
        raise RuntimeError("failed to load native library")

    # Pex_Version
    lib.Pex_Version_IsCompatible.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.Pex_Version_IsCompatible.restype = ctypes.c_bool

    if not lib.Pex_Version_IsCompatible(MAJOR_VERSION, MINOR_VERSION):
        raise RuntimeError("bindings not compatible with native library")

    # Pex_Init
    lib.Pex_Init.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.Pex_Init.restype = None

    lib.Pex_Cleanup.argtypes = []
    lib.Pex_Cleanup.restype = None

    # Pex_Lock
    lib.Pex_Lock.argtypes = []
    lib.Pex_Lock.restype = None

    lib.Pex_Unlock.argtypes = []
    lib.Pex_Unlock.restype = None

    # Pex_Status
    lib.Pex_Status_New.argtypes = []
    lib.Pex_Status_New.restype = ctypes.POINTER(_Pex_Status)

    lib.Pex_Status_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_Pex_Status))]
    lib.Pex_Status_Delete.restype = None

    lib.Pex_Status_OK.argtypes = [ctypes.POINTER(_Pex_Status)]
    lib.Pex_Status_OK.restype = ctypes.c_bool

    lib.Pex_Status_GetCode.argtypes = [ctypes.POINTER(_Pex_Status)]
    lib.Pex_Status_GetCode.restype = ctypes.c_int

    lib.Pex_Status_GetMessage.argtypes = [ctypes.POINTER(_Pex_Status)]
    lib.Pex_Status_GetMessage.restype = ctypes.c_char_p

    lib.Pex_Status_IsRetryable.argtypes = [ctypes.POINTER(_Pex_Status)]
    lib.Pex_Status_IsRetryable.restype = ctypes.c_bool

    # Pex_Buffer
    lib.Pex_Buffer_New.argtypes = []
    lib.Pex_Buffer_New.restype = ctypes.POINTER(_Pex_Buffer)

    lib.Pex_Buffer_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_Pex_Buffer))]
    lib.Pex_Buffer_Delete.restype = None

    lib.Pex_Buffer_Set.argtypes = [
        ctypes.POINTER(_Pex_Buffer),
        ctypes.c_void_p,
        ctypes.c_size_t,
    ]
    lib.Pex_Buffer_Set.restype = None

    lib.Pex_Buffer_GetData.argtypes = [ctypes.POINTER(_Pex_Buffer)]
    lib.Pex_Buffer_GetData.restype = ctypes.c_void_p

    lib.Pex_Buffer_GetSize.argtypes = [ctypes.POINTER(_Pex_Buffer)]
    lib.Pex_Buffer_GetSize.restype = ctypes.c_size_t

    # Pex_Fingerprint
    lib.Pex_Fingerprint_File.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Status),
        ctypes.c_int,
    ]
    lib.Pex_Fingerprint_File.restype = None

    lib.Pex_Fingerprint_Buffer.argtypes = [
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Status),
        ctypes.c_int,
    ]
    lib.Pex_Fingerprint_Buffer.restype = None

    lib.Pex_FingerprintFile.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.c_char_p,
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Status),
        ctypes.c_int,
    ]
    lib.Pex_FingerprintFile.restype = None

    lib.Pex_FingerprintBuffer.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Status),
        ctypes.c_int,
    ]
    lib.Pex_FingerprintBuffer.restype = None

    # Pex_Client
    lib.Pex_Client_New.argtypes = []
    lib.Pex_Client_New.restype = ctypes.POINTER(_Pex_Client)

    lib.Pex_Client_Delete.argtypes = [ctypes.POINTER(ctypes.POINTER(_Pex_Client))]
    lib.Pex_Client_Delete.restype = None

    lib.Pex_Client_Init.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(_Pex_Status),
    ]
    lib.Pex_Client_Init.restype = None

    # Pex_StartSearch
    lib.Pex_StartSearch.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.POINTER(_Pex_StartSearchRequest),
        ctypes.POINTER(_Pex_StartSearchResult),
        ctypes.POINTER(_Pex_Status),
    ]
    lib.Pex_StartSearch.restype = None

    # Pex_CheckSearch
    lib.Pex_CheckSearch.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.POINTER(_Pex_CheckSearchRequest),
        ctypes.POINTER(_Pex_CheckSearchResult),
        ctypes.POINTER(_Pex_Status),
    ]
    lib.Pex_CheckSearch.restype = None

    # Pex_StartSearchRequest
    lib.Pex_StartSearchRequest_New.argtypes = []
    lib.Pex_StartSearchRequest_New.restype = ctypes.POINTER(
        _Pex_StartSearchRequest
    )

    lib.Pex_StartSearchRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_Pex_StartSearchRequest))
    ]
    lib.Pex_StartSearchRequest_Delete.restype = None

    lib.Pex_StartSearchRequest_SetType.argtypes = [
        ctypes.POINTER(_Pex_StartSearchRequest),
        ctypes.c_int,
    ]
    lib.Pex_StartSearchRequest_SetType.restype = None

    lib.Pex_StartSearchRequest_SetFingerprint.argtypes = [
        ctypes.POINTER(_Pex_StartSearchRequest),
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Status),
    ]
    lib.Pex_StartSearchRequest_SetFingerprint.restype = None

    # Pex_StartSearchResult
    lib.Pex_StartSearchResult_New.argtypes = []
    lib.Pex_StartSearchResult_New.restype = ctypes.POINTER(
        _Pex_StartSearchResult
    )

    lib.Pex_StartSearchResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_Pex_StartSearchResult))
    ]
    lib.Pex_StartSearchResult_Delete.restype = None

    lib.Pex_StartSearchResult_NextLookupID.argtypes = [
        ctypes.POINTER(_Pex_StartSearchResult),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_char_p),
    ]
    lib.Pex_StartSearchResult_NextLookupID.restype = ctypes.c_bool

    # Pex_CheckSearchRequest
    lib.Pex_CheckSearchRequest_New.argtypes = []
    lib.Pex_CheckSearchRequest_New.restype = ctypes.POINTER(
        _Pex_CheckSearchRequest
    )

    lib.Pex_CheckSearchRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_Pex_CheckSearchRequest))
    ]
    lib.Pex_CheckSearchRequest_Delete.restype = None

    lib.Pex_CheckSearchRequest_AddLookupID.argtypes = [
        ctypes.POINTER(_Pex_CheckSearchRequest),
        ctypes.c_char_p,
    ]
    lib.Pex_CheckSearchRequest_AddLookupID.restype = None

    # Pex_CheckSearchResult
    lib.Pex_CheckSearchResult_New.argtypes = []
    lib.Pex_CheckSearchResult_New.restype = ctypes.POINTER(
        _Pex_CheckSearchResult
    )

    lib.Pex_CheckSearchResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_Pex_CheckSearchResult))
    ]
    lib.Pex_CheckSearchResult_Delete.restype = None

    lib.Pex_CheckSearchResult_GetJSON.argtypes = [
        ctypes.POINTER(_Pex_CheckSearchResult),
    ]
    lib.Pex_CheckSearchResult_GetJSON.restype = ctypes.c_char_p

    # Pex_ListRequest
    lib.Pex_ListRequest_New.argtypes = []
    lib.Pex_ListRequest_New.restype = ctypes.POINTER(
        _Pex_ListRequest
    )

    lib.Pex_ListRequest_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_Pex_ListRequest))
    ]
    lib.Pex_ListRequest_Delete.restype = None

    lib.Pex_ListRequest_SetAfter.argtypes = [
        ctypes.POINTER(_Pex_ListRequest),
        ctypes.c_char_p,
    ]
    lib.Pex_ListRequest_SetAfter.restype = None

    lib.Pex_ListRequest_SetLimit.argtypes = [
        ctypes.POINTER(_Pex_ListRequest),
        ctypes.c_int,
    ]
    lib.Pex_ListRequest_SetLimit.restype = None

    # Pex_ListResult
    lib.Pex_ListResult_New.argtypes = []
    lib.Pex_ListResult_New.restype = ctypes.POINTER(
        _Pex_ListResult
    )

    lib.Pex_ListResult_Delete.argtypes = [
        ctypes.POINTER(ctypes.POINTER(_Pex_ListResult))
    ]
    lib.Pex_ListResult_Delete.restype = None

    lib.Pex_ListResult_GetJSON.argtypes = [
        ctypes.POINTER(_Pex_ListResult),
    ]
    lib.Pex_ListResult_GetJSON.restype = ctypes.c_char_p

    # Pex_Ingest
    lib.Pex_Ingest.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.c_char_p,
        ctypes.POINTER(_Pex_Buffer),
        ctypes.POINTER(_Pex_Status),
    ]
    lib.Pex_Ingest.restype = None

    # Pex_Archive
    lib.Pex_Archive.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.POINTER(_Pex_Status),
    ]
    lib.Pex_Archive.restype = None

    # Pex_List
    lib.Pex_List.argtypes = [
        ctypes.POINTER(_Pex_Client),
        ctypes.POINTER(_Pex_ListRequest),
        ctypes.POINTER(_Pex_ListResult),
        ctypes.POINTER(_Pex_Status),
    ]
    lib.Pex_List.restype = None

    return lib


_lib = _load_lib()
