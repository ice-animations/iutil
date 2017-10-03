import re
import os
from collections import namedtuple
import subprocess

from ntfslink import symlinks as syml
from ntfslink import junctions as junc

symlinkdPattern = re.compile(
    r'^(?:.*)(?P<stype><SYMLINKD?>|<JUNCTION>)(?:\s+)(?P<name>.*)(?:\s+\[)'
    r'(?P<target>.*)(?:\]\s*)$')

symlinkMapping = namedtuple('symlinkMapping', 'location name target stype')


def normpath(path):
    ''' Convert path to a standardized format '''
    path = os.path.normpath(path)
    path = os.path.normcase(path)
    while path.endswith(os.sep):
        path = path[:-1]
    return path


def getSymlinks2(dirpath):
    ''' get symlink mapping by popen method
    :type dirpath: str
    '''
    maps = []
    dirpath = normpath(os.path.realpath(dirpath))

    if not os.path.exists(dirpath):
        raise ValueError("Directory %s does not exists" % dirpath)
    if not os.path.isdir(dirpath):
        raise ValueError("%s is not a directory" % dirpath)

    commandargs = ['dir']
    commandargs.append('"%s"' % dirpath)
    commandargs.append('/al')
    pro = subprocess.Popen(
        ' '.join(commandargs), shell=1, stdout=subprocess.PIPE)

    for line in pro.stdout.readlines():
        match = symlinkdPattern.match(line)
        if not match:
            continue
        name = match.group('name')
        target = normpath(match.group('target'))
        stype = match.group('stype')
        maps.append(symlinkMapping(dirpath, name, target, stype))
    return maps


def getSymlinks(dirpath):
    ''' get symlink mappings by ctypes method
    :type dirpath: str
    '''
    maps = []
    dirpath = normpath(os.path.realpath(dirpath))

    if not os.path.exists(dirpath):
        raise ValueError("Directory %s does not exists" % dirpath)
    if not os.path.isdir(dirpath):
        raise ValueError("%s is not a directory" % dirpath)

    for name in os.listdir(dirpath):
        path = os.path.join(dirpath, name)
        if syml.check(path):
            maps.append(
                symlinkMapping(dirpath, name,
                               normpath(syml.read(path)), '<SYMLINKD>'))
        elif junc.check(path):
            maps.append(
                symlinkMapping(dirpath, name,
                               normpath(junc.read(path)), '<JUNCTION>'))

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


def translatePath(path, maps=None, linkdir=None, reverse=False, single=True):
    '''
    :type path: str
    :type maps: None or list of symlinkMapping
    :type linkdir: None or str
    :type single: bool
    '''
    paths = []
    path = os.path.normpath(path.strip())
    if maps is None:
        if linkdir is not None and os.path.exists(linkdir):
            maps = getSymlinks(linkdir)
        else:
            raise ValueError('linkdir is invalid')

    for m in maps:
        linkpath = os.path.join(m.location, m.name)

        tofind, toreplace = linkpath, m.target
        if reverse:
            tofind, toreplace = toreplace, tofind

        tofind += '\\'
        toreplace += '\\'
        tofind = '^' + tofind.replace('\\', r'\\')
        toreplace = toreplace.replace('\\', r'\\')
        if re.search(tofind, path, re.IGNORECASE):
            newpath = re.sub(tofind, toreplace, path, 1, re.I)
            paths.append(newpath)

    if single:
        return paths[0] if paths else path
    else:
        return paths


def test():
    maps = getSymlinks(r'\\dbserver\assets')
    print translatePath(
        '\\\\dbserver\\assets\\captain_khalfan\\02_production'
        '\\ep09\\assets\\character\\captain_khalfan_regular\\rig'
        '\\captain_khalfan_regular_rig.ma',
        maps,
        single=False)


if __name__ == '__main__':
    test()
