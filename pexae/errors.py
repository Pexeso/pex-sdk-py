# Copyright 2020 Pexeso Inc. All rights reserved.

from enum import Enum

from pexae.lib import _lib


class Code(Enum):
    """
    Error codes that are associated with :class:`~AEError`.
    """

    OK = 0
    DEADLINE_EXCEEDED = 1
    PERMISSION_DENIED = 2
    UNAUTHENTICATED = 3
    NOT_FOUND = 4
    INVALID_INPUT = 5
    OUT_OF_MEMORY = 6
    INTERNAL_ERROR = 7
    NOT_INITIALIZED = 8
    CONNECTION_ERROR = 9
    LOOKUP_FAILED = 10
    LOOKUP_TIMED_OUT = 11


class AEError(RuntimeError):
    """
    An instance of this class will be raised by a number of the SDK calls.
    """

    @staticmethod
    def check(code, message):
        c = Code(code)
        if c != Code.OK:
            raise AEError(c, message)

    @staticmethod
    def check_status(c_status):
        if not _lib.AE_Status_OK(c_status.get()):
            raise AEError.from_status(c_status)

    @staticmethod
    def from_status(c_status):
        code = _lib.AE_Status_GetCode(c_status.get())
        message = _lib.AE_Status_GetMessage(c_status.get())
        return AEError(Code(code), message.decode())

    def __init__(self, code, message):
        super().__init__("{}: {}".format(code, message))
        self._code = Code(code)
        self._message = message

    @property
    def code(self):
        """
        An error code that can be used to determine why the error was raised.
        See :class:`~Code` to find out what codes are available.
        """
        return self._code

    @property
    def message(self):
        """
        Human readable error message. Mostly useful for logging and debugging.
        """
        return self._message
