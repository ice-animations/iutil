
import re
import os
from collections import namedtuple
import subprocess

symlinkdPattern = re.compile(r'^(?:.*)(?P<stype><SYMLINKD?>|<JUNCTION>)(?:\s+)(?P<name>.*)(?:\s+\[)'
        r'(?P<target>.*)(?:\]\s*)$')

symlinkMapping = namedtuple('symlinkMapping', 'location name target stype')


def normpath(path):
    path = os.path.normpath(path)
    path = os.path.normcase(path)
    while path.endswith(os.sep):
        path = path[:-1]
    return path


def getSymlinks(dirpath):
    '''
    :type dirpath: str
    '''
    maps = []
    dirpath = normpath(os.path.realpath(dirpath))

    if not os.path.exists(dirpath):
        raise ValueError, "Directory %s does not exists" % dirpath
    if not os.path.isdir(dirpath):
        raise ValueError, "%s is not a directory" % dirpath

    commandargs = ['dir']
    commandargs.append('"%s"'%dirpath)
    commandargs.append('/al')
    pro = subprocess.Popen(' '.join(commandargs), shell=1, stdout=subprocess.PIPE)

    for line in pro.stdout.readlines():
        match = symlinkdPattern.match(line)
        if not match:
            continue
        name = match.group('name')
        target = normpath(match.group('target'))
        stype = match.group('stype')
        maps.append(symlinkMapping(dirpath, name, target, stype))
    return maps


def translateSymlink(path, maps=None):
    '''
    :type path: str
    :type maps: None or list of symlinkMapping
    '''
    path = os.path.normpath(path)
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    if maps is None:
        maps = getSymlinks(dirname)
    for m in maps:
        if m.location == dirname and m.name == basename:
            return m.target
    return path


def translatePath(path, maps=None, linkdir=None):
    '''
    :type path: str
    :type maps: None or list of symlinkMapping
    :type linkdir: None or str
    '''
    path = normpath(path)
    if maps is None:
        if linkdir is not None and os.path.exists(linkdir):
            maps = getSymlinks(linkdir)
        else:
            raise ValueError, 'linkdir is invalid'

    for m in maps:
        linkpath = os.path.join(m.location, m.name)
        if path.startswith(linkpath):
            return path.replace(linkpath, m.target, 1)
    return path


if __name__ == '__main__':
    maps = getSymlinks(r'\\dbserver\assets')
    print translatePath(r'\\dbserver\assets\test_mansour_ep\assets\character',
            maps)
