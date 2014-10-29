import subprocess
import re
from collections import namedtuple

import os
import string
from ctypes import windll

netusePattern = re.compile(r'(?P<status>OK|UnAvailable)(?:\s+)(?P<drive>[a-zA-Z]:)(?:\s+)(?P<target>.+?)(?:\s+)(?:Microsoft Windows Network|)(?:\s+)')
drivemapping = namedtuple('drivemapping', 'status drive target')

def getNetworkMaps():
    maps = {}
    pro = subprocess.Popen('net use', shell=1, stdout=subprocess.PIPE)
    out = pro.stdout.readlines()
    for line in out:
        match = netusePattern.match(line)
        if match:
            dm = drivemapping(*match.groups())
            maps[dm.drive]=dm

    return maps


def getDrives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter + ':')
        bitmask >>= 1

    return drives


drivePattern = re.compile(r'^(?P<drive>[A-Za-z]:)')


def getDriveMapping(drive, maps=None):
    '''
    :type drive: str or unicode
    :rtype: dict
    '''
    if not drivePattern.match(drive):
        raise ValueError, "Not a Valid Drive '%s'" %drive
    drive = drive.upper()
    if drive not in getDrives():
        return None
    if not maps:
        maps = getNetworkMaps()
    return maps.get(drive, None)


def translateMappedtoUNC(path, maps=None):
    '''
    :type path: str or unicode
    '''
    drive = getDrive(path)
    if not isValidDrive(drive):
        return path
    if not maps:
        maps = getNetworkMaps()
    mapping = getDriveMapping(drive, maps)
    if mapping:
        path = path.replace(drive, mapping.target, 1)
    return path


def getDrive(path=None):
    if not path: path=os.curdir()
    match = drivePattern.search(path)
    if not match:
        return ''
    return match.group('drive')


def isValidDrive(drive):
    if not drivePattern.match(drive):
        return False
    drive = drive.upper()
    if drive in getDrives():
        return True
    return False


def isMappedNetworkPath(path, maps=None):
    '''
    :type path: str or unicode
    '''
    drive = getDrive(path)
    if not drive:
        return False
    if not maps:
        maps = getNetworkMaps()
    return maps.has_key(drive)


if __name__ == '__main__':
    path = r'P:\external\Projects'
    print getDrive(path)
    nmaps = getNetworkMaps()
    if isMappedNetworkPath(path, nmaps):
        print getDriveMapping(getDrive(path), nmaps).target
        print translateMappedtoUNC(path, nmaps)

