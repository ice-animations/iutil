from .createprocess import CreateProcessWithLogonW, waitForChild

import os
import logging
import logging.handlers
from .networkmaps import getNetworkMaps, translateMappedtoUNC

__all__ = ['powercopy', 'PowerCopyError']

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__mydir__ = os.path.dirname(__file__)
_cred = os.path.join(__mydir__, '.pccred')
_mod = 'copyallfiles.py'

module = os.path.join(os.path.realpath(__mydir__), _mod)
executable = r"R:\Pipe_Repo\Users\Qurban\applications\Python27\pythonw.exe"

maps = getNetworkMaps()
module = translateMappedtoUNC(module, maps)
executable = translateMappedtoUNC(executable, maps)


class PowerCopyError(Exception):
    def __init__(self, errorcode, command):
        self.errorcode = errorcode
        self.command = command
        self.strerror = os.strerror(errorcode)

    def __str__(self):
        return "Error code '%d' in copy process %s\nreason: %s" % (
            self.errorcode, self.command, self.strerror)


def _getImpersonationData():
    return 'iceanimations.com', 'tactic', 'tactic123'


def cmdargEscape(arg):
    while arg.endswith('\\'):
        arg = arg[:-1]
    arg = arg.replace('"', r'\"')
    if arg.find(' ') >= 0:
        arg = '"%s"' % arg
    return arg


def powercopy(fromdir, todir, tree=False):

    dom, us, pw = _getImpersonationData()

    commandargs = []
    commandargs.append(cmdargEscape(executable))
    commandargs.append(cmdargEscape(module))
    commandargs.append(cmdargEscape(fromdir))
    commandargs.append(cmdargEscape(todir))
    if tree:
        commandargs.append(cmdargEscape('--tree'))
    command = ' '.join(commandargs)

    pi = CreateProcessWithLogonW(
        lpUsername=us,
        lpDomain=dom,
        lpPassword=pw,
        dwLogonFlags=0,
        lpApplicationName=None,
        lpCommandLine=command,
        dwCreationFlags=0,
        lpEnvironment=None,
        lpCurrentDirectory=None,
        startupInfo=None)

    exitcode = waitForChild(pi).value
    if exitcode:
        raise PowerCopyError(exitcode, command)
    return exitcode


def test_powercopy():
    import time
    todir = r'\\nasx\Storage\Projects\external\Al_Mansour_Season_02\test_run\assets\environment\ep_16\testEnv'
    #todir = r'\\dbserver\assets\test_mansour_ep\assets\environment\ep_16\testEnv'
    fromdir = r"D:\Wooden Box\Tex\Gump"

    k = time.time()
    powercopy(fromdir, todir)
    logger.debug(time.time() - k)

    import subprocess
    subprocess.call("start explorer %s" % todir, shell=1)


if __name__ == '__main__':
    test_powercopy()
