__all__ = ['CreateProcessWithLogonW', 'waitForChild']

from ctypes import (windll, create_unicode_buffer, sizeof, byref, WinError,
        c_int, pointer)
from ctypes.wintypes import (HANDLE, DWORD, WORD, LPWSTR, Structure, POINTER,
        Array, LPCWSTR, BOOL, BYTE)

INVALID_HANDLE_VALUE = -1
CREATE_UNICODE_ENVIRONMENT = 0x00000400

CData = Array.__base__
LPBYTE = POINTER(BYTE)

class PROCESS_INFORMATION(Structure):
    '''http://msdn.microsoft.com/en-us/library/ms684873'''
    _fields_ = [
        ('hProcess',    HANDLE),
        ('hThread',     HANDLE),
        ('dwProcessId', DWORD),
        ('dwThreadId',  DWORD),
    ]
LPPROCESS_INFORMATION = POINTER(PROCESS_INFORMATION)


class STARTUPINFOW(Structure):
    'http://msdn.microsoft.com/en-us/library/ms686331'
    _fields_ = [
        ('cb',              DWORD),
        ('lpReserved',      LPWSTR),
        ('lpDesktop',       LPWSTR),
        ('lpTitle',         LPWSTR),
        ('dwX',             DWORD),
        ('dwY',             DWORD),
        ('dwXSize',         DWORD),
        ('dwYSize',         DWORD),
        ('dwXCountChars',   DWORD),
        ('dwYCountChars',   DWORD),
        ('dwFillAttribute', DWORD),
        ('dwFlags',         DWORD),
        ('wShowWindow',     WORD),
        ('cbReserved2',     WORD),
        ('lpReserved2',     LPBYTE),
        ('hStdInput',       HANDLE),
        ('hStdOutput',      HANDLE),
        ('hStdError',       HANDLE),
    ]
LPSTARTUPINFOW = POINTER(STARTUPINFOW)


# http://msdn.microsoft.com/en-us/library/ms682431
windll.advapi32.CreateProcessWithLogonW.restype = BOOL
windll.advapi32.CreateProcessWithLogonW.argtypes = [
    LPCWSTR, # lpUsername
    LPCWSTR, # lpDomain
    LPCWSTR, # lpPassword
    DWORD,   # dwLogonFlags
    LPCWSTR, # lpApplicationName
    LPWSTR,  # lpCommandLine (inout)
    DWORD,   # dwCreationFlags
    LPCWSTR, # lpEnvironment  (force Unicode)
    LPCWSTR, # lpCurrentDirectory
    LPSTARTUPINFOW, # lpStartupInfo
    LPPROCESS_INFORMATION, # lpProcessInfo (out)
]

def CreateProcessWithLogonW(
    lpUsername=None,
    lpDomain=None,
    lpPassword=None,
    dwLogonFlags=0,
    lpApplicationName=None,
    lpCommandLine=None,
    dwCreationFlags=0,
    lpEnvironment=None,
    lpCurrentDirectory=None,
    startupInfo=None
):
    if (lpCommandLine is not None and
        not isinstance(lpCommandLine, CData)
    ):
        lpCommandLine = create_unicode_buffer(lpCommandLine)
    dwCreationFlags |= CREATE_UNICODE_ENVIRONMENT
    if startupInfo is None:
        startupInfo = STARTUPINFOW(sizeof(STARTUPINFOW))
    processInformation = PROCESS_INFORMATION(
        INVALID_HANDLE_VALUE, INVALID_HANDLE_VALUE)
    success = windll.advapi32.CreateProcessWithLogonW(
        lpUsername, lpDomain, lpPassword, dwLogonFlags, lpApplicationName,
        lpCommandLine, dwCreationFlags, lpEnvironment, lpCurrentDirectory,
        byref(startupInfo), byref(processInformation))
    if not success:
        #print windll.kernel32.GetLastError()
        raise WinError()
    return processInformation

def waitForChild(processInformation):
    INFINITE = -1
    exitCode = c_int(0)
    pexitCode = pointer(exitCode)

    windll.kernel32.WaitForSingleObject( processInformation.hProcess,
            INFINITE);
    ec_success = windll.kernel32.GetExitCodeProcess(processInformation.hProcess,
            pexitCode);

    windll.kernel32.CloseHandle( processInformation.hProcess );
    windll.kernel32.CloseHandle( processInformation.hThread );

    if not ec_success:
        raise Exception, windll.kernel32.GetLastError()

    return exitCode

