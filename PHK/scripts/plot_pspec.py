#! /usr/bin/env python

import numpy as np
import sys
import PHK
from capo import pspec
from pylab import *

#set things here
parent_dir = sys.argv[1]
#seps = ['0,1','1,1','-1,1','2,1','-2,1','3,1','-3,1']
seps = ['0,1','1,1','-1,1']
#seps = ['0,2','1,2','-1,2']
#seps = ['0,3','1,3','-1,3']
#seps = ['0,4','1,4','-1,4']
#seps = PHK.gen_all_seps()
pols = 'IQUV'
figheight=6.
Tsys = 560.*np.sqrt(20./55.)

#do all the things:
Pfig = figure(figsize=(2*figheight, figheight))
Pax = Pfig.add_subplot(121)
Dax = Pfig.add_subplot(122)

D = PHK.PspecDir(parent_dir=PHK.get_parent(sys.argv[1]))
for parent in D.tree:
    for poldir in sorted(D.tree[parent]):
        K,Pk,Dk,dPk,dDk = None,{},{},{},{}
        pol = poldir.split('/')[-1]
        if not pol in pols:
            continue
        for init in 'p':
            for sepdir in D.tree[parent][poldir]:
                sep = sepdir.split('/')[-1]
                if not sep in seps or sep == 'all':
                    continue
                Pfile = '%s/%sspec.npz'%(sepdir,init)
                figdata = np.load(Pfile)
                wgt = np.abs(figdata['dPk'])**-2
                if K is None:
                    K = figdata['Kpl']
                try:
                    Pk[init] += figdata['Pk'] * wgt
                    dPk[init] += wgt
                except(KeyError):
                    Pk[init] = figdata['Pk'] * wgt
                    dPk[init] = wgt

            Pk[init] /= dPk[init]
            dPk[init] = np.sqrt(1./dPk[init])
            if init == 'n':
                noise_level = np.mean([p for p in Pk[init] if not np.isnan(p)])
                noise_level *= (Tsys/560.)**2
                Pk[init] = np.ones_like(Pk[init])*noise_level

            Dk[init] = PHK.P2D(K, 0., Pk[init])
            dDk[init] = PHK.P2D(K, 0., dPk[init])

            if init == 'n':
                Pax.plot(K,Pk[init].real, '0.5')
                Dax.plot(K,Dk[init].real, '0.5')
            else:
                Pax.errorbar(K,Pk[init].real, yerr=dPk[init], label=pol, fmt='.-')
                Dax.errorbar(K,Dk[init].real, yerr=dDk[init], label=pol, fmt='.-')

Pax.legend()
Dax.legend()
Pax.set_yscale('log')
Dax.set_yscale('log')

Pfig.suptitle(PHK.get_parent(sys.argv[1]))
outfile = "%s/IQUV.eps"%D.tree.keys()[0]
Pfig.savefig(outfile, fmt='eps')

show()
