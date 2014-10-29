import sys
import shutil
import os
import traceback

try:
    fromdir = sys.argv[1]
    todir = sys.argv[2]

    copy = shutil.copy2

    tree=False
    if '--tree' in sys.argv[3:]:
        tree=True
        copy = shutil.copytree

    fromfiles = [fromdir]
    if os.path.isdir(fromdir):
        if tree:
            copy=shutil.copytree
        else:
            fromfiles = [os.path.join(fromdir,f) for f in os.listdir(fromdir)
                    if os.path.isfile(os.path.join(fromdir,f))]

    if os.path.isfile(todir) and len(fromfiles) > 1:
        todir = os.path.dirname(todir)

    for fromfile in fromfiles:
        copy(fromfile, todir)

except BaseException as be:
    err = traceback.format_exc()
    sys.stderr.write(err)
    sys.exit(be.errno)


