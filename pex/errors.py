# Copyright 2023 Pexeso Inc. All rights reserved.

from enum import Enum

from pex.lib import _lib


class Code(Enum):
    """
    Error codes that are associated with :class:`~Error`.
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
    RESOURCE_EXHAUSTED = 12


class Error(RuntimeError):
    """
    An instance of this class will be raised by a number of the SDK calls.
    """

    @staticmethod
    def check(code, message):
        c = Code(code)
        if c != Code.OK:
            raise Error(c, message)

    @staticmethod
    def check_status(c_status):
        if not _lib.Pex_Status_OK(c_status.get()):
            raise Error.from_status(c_status)

    @staticmethod
    def from_status(c_status):
        code = _lib.Pex_Status_GetCode(c_status.get())
        message = _lib.Pex_Status_GetMessage(c_status.get())
        is_retryable = _lib.Pex_Status_IsRetryable(c_status.get())
        return Error(Code(code), message.decode(), is_retryable)

    def __init__(self, code, message, is_retryable=False):
        super().__init__("{}: {}".format(code, message))
        self._code = Code(code)
        self._message = message
        self._is_retryable = is_retryable

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

    @property
    def is_retryable(self):
        """
        Returns True if retrying the operation might eventually succeed.
        """
        return self._is_retryable
