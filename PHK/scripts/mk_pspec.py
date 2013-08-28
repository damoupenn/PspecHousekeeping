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
args = ' '.join(args)

COMMAND = 'python pspec_redmult_cov.py %s -a %s -p %s -c %s'
pwd = os.getcwd()

D = PHK.PspecDir(parent_dir=opts.name, seps=seps)
try:
    for parent in D.tree:
        for poldir in D.tree[parent]:
            if poldir.split('/')[-1] in opts.pol.split(','):
                _pol = poldir.split('/')[-1]
                for sepdir in D.tree[parent][poldir]:
                    print "Writing data to %s"%sepdir
                    sep = sepdir.split('/')[-1]
                    if sep == '0,0':
                        continue
                    antstr = PHK.sep2bl([sep])[0]
                    print COMMAND%(args, antstr, _pol, opts.chan)
                    sp.call(COMMAND%(args, antstr, _pol, opts.chan), shell=True)
                    sp.call('mv pspec_boot*.npz %s'%sepdir, shell=True)
                    sp.call('mv nspec_boot*.npz %s'%sepdir, shell=True)
    D.cleanup()
except(KeyboardInterrupt):
    sys.exit()
