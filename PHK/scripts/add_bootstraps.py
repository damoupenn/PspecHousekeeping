#! /usr/bin/env python

import PHK
import numpy as np
import sys
import os

def get_parent():
    try:
        parent = sys.argv[1]
        if parent[-1] == '/':
            parent = parent[:-1]
        return parent
    except(IndexError):
        print "Directory of power spectra needed!"
        sys.exit(1)

D = PHK.PspecDir(parent_dir=get_parent())

for parent in D.tree:
    for poldir in D.tree[parent]:
        for sepdir in D.tree[parent][poldir]:
            try:
                k,Pk,Pn = None,[],[]
                if os.path.exists(sepdir+'/nspec.npz'):
                    print 'File exists, skipping %s'%sepdir
                    continue

                for bs in map(lambda x: '%s/%s'%(sepdir, x), PHK.ls(sepdir)):
                    filedata = np.load(bs)
                    if k is None:
                        k = filedata['kpl']
                    if bs.startswith('nspec'):
                        Pn.append(filedata['pk'])
                    elif bs.startswith('pspec'):
                        Pk.append(filedata['pk'])
                    filedata.close()
                #multiply by scaling factors:
                scaling = 2.35 * 0.66 #beam-squared * pictor calibration error
                Pn = scaling*np.array(Pn)
                Pk = scaling*np.array(Pk)

                np.savez(sepdir+'/nspec.npz', Kpl=k, Pk=np.mean(Pn, axis=0), dPk=np.std(Pn, axis=0))
                np.savez(sepdir+'/pspec.npz', Kpl=k, Pk=np.mean(Pk, axis=0), dPk=np.std(Pk, axis=0))
            except(IOError):
                print 'ERROR: %s'%sepdir
