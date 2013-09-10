#! /usr/bin/env python

import PHK
from aipy import scripting
import optparse
import os
import sys
import subprocess as sp

o = optparse.OptionParser()
scripting.add_standard_options(o, pol=True, chan=True, cal=True)
o.add_option('--name', dest='name', default='MySpec',
        help='Name of output directory. [MySpec]')
o.add_option('--seps',dest='seps',default='0,1',
        help="bl types to use in row,col;row,col format")
opts, args = o.parse_args()

if opts.seps == 'all':
    seps = PHK.gen_all_seps(calfile=opts.cal)
else:
    seps = opts.seps.split(';')

COMMAND = 'python pspec_redmult_cov.py %s -a %s -p %s -c %s'
pwd = os.getcwd()

def lst_from_filename(filename):
    return filename.split('.')[-2]

try:
    for f in args:
        print "Reading %s"%f
        print '='*35

        D = PHK.PspecDir(parent_dir="LST_%s"%lst_from_filename(f), seps=seps, new=True)
        for parent in D.tree:
            for poldir in D.tree[parent]:
                if poldir.split('/')[-1] in opts.pol.split(','):
                    print poldir
                    _pol = poldir.split('/')[-1]
                    for sepdir in D.tree[parent][poldir]:
                        sep = sepdir.split('/')[-1]
                        if sep == '0,0':
                            continue
                        if not sep in seps:
                            continue
                        if os.path.exists('%s/pspec.npz'%sepdir):
                            print sep, "file exists"
                            continue
                        print "Writing data to %s"%sepdir
                        antstr = PHK.sep2bl([sep])[0]
                        print COMMAND%(f, antstr, _pol, opts.chan)
                        sp.call(COMMAND%(f, antstr, _pol, opts.chan), shell=True)
                        sp.call('mv pspec_boot*.npz %s'%sepdir, shell=True)
                        sp.call('mv nspec_boot*.npz %s'%sepdir, shell=True)
        D.cleanup()
except(KeyboardInterrupt):
    print 'Exited on command.'
    sys.exit()
