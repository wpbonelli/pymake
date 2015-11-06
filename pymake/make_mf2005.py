from __future__ import print_function
import os
import shutil
import pymake
from download import download_and_unzip


# Download the MODFLOW-2005 distribution
url = "http://water.usgs.gov/ogw/modflow/MODFLOW-2005_v1.11.00/mf2005v1_11_00_unix.zip"
download_and_unzip(url)

# Rename Unix to a more reasonable name
dirname = 'MF2005.1_11u'
if os.path.isdir(dirname):
    shutil.rmtree(dirname)
os.rename('Unix', 'MF2005.1_11u')

# Remove two src folders
srcdir = os.path.join(dirname, 'src')
dlist = ['hydprograms', 'mnw1to2']
for d in dlist:
    dname = os.path.join(srcdir, d)
    if os.path.isdir(dname):
        print('Removing ', dname)
        shutil.rmtree(os.path.join(srcdir, d))

target = 'mf2005dbl'
pymake.main(srcdir, target, 'gfortran', makeclean=True, expedite=False,
            dryrun=False, double=True, debug=False)
