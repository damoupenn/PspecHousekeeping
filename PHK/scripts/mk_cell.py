#! /usr/bin/env python

import PHK
import sys
import numpy as np
from capo import pspec
from pylab import *

parent=PHK.get_parent(sys.argv[1])
pols='IQUV'

fq = np.median(np.linspace(0.1,0.2,203)[110:149])
colors = {'I':'k','Q':'b', 'U':'r', 'V':'c'}

fig = figure()
ax = fig.add_subplot(111)
D = PHK.PspecDir(parent_dir=parent)
ELL, C_ELL, C_ERR = {},{},{}
for parentdir in D.tree:
    for poldir in D.tree[parentdir]:
        pol = poldir.split('/')[-1]
        if not pol in pols:
            continue
        for sepdir in D.tree[parentdir][poldir]:
            sepstr = sepdir.split('/')[-1]
            u,v = PHK.uv_from_sep(sepstr)
            ell = 2.*np.pi*np.sqrt(u**2+v**2)*(fq/0.3)

            #read in data
            datafile = np.load('%s/pspec.npz'%(sepdir))
            try:
                zero = np.where(datafile['Kpl']==0)
                Pk = datafile['Pk'][zero]
                dPk = datafile['dPk'][zero]
            except(ValueError,IndexError):
                continue

            #scale it
            scalar = 1./pspec.X2Y(fq)
            #scalar *= ell*(ell+1)/(2.*np.pi)

            Pk *= scalar
            dPk *= scalar

            #plot it
            ax.errorbar(ell, Pk, yerr=dPk, ecolor=colors[pol])
            datafile.close()

            #save data?
            ELL[pol] = ELL.get(pol,[]) + [ell]
            C_ELL[pol] = C_ELL.get(pol,[]) + [Pk]
            C_ERR[pol] = C_ERR.get(pol,[]) + [dPk]

ax.set_yscale('log')
ax.set_xscale('log')

def C2D(l,Cl):
    return 0.5 * l * (l+1.) * Cl / np.pi

fig2 = figure()
ax2 = fig2.add_subplot(111)
for pol in ELL:
    ell,dell,cell,dcell = [],[],[],[]

    #sort data by ell
    inds = np.argsort(ELL[pol])
    ELL[pol]   = np.array(  ELL[pol]).take(inds)
    C_ELL[pol] = np.array(C_ELL[pol]).take(inds)
    C_ERR[pol] = np.array(C_ERR[pol]).take(inds)

    print "===%s==="%pol
    #where are the obvious demarcations of data?
    N = len(ELL[pol])
    tol = 1. #nsigma above which we call a 'jump'
    diff = np.diff(ELL[pol])
    diff /= np.std(diff)
    is_jump = np.where(np.abs(diff) >= tol)
    inds = 0.5 * (np.arange(N)[:-1] + np.arange(N)[1:])
    breaks = [0] + list(inds.take(is_jump)[0]) + [N]

    Ngrp = len(breaks) - 1
    print "\tbreaking up data into %d chunks..."%Ngrp
    #add up each group
    for i in range(Ngrp):
        this_grp = [j >= breaks[i] and j < breaks[i+1] for j in range(N)]
        _ell = np.extract(this_grp, ELL[pol])
        _cell = np.extract(this_grp, C_ELL[pol])
        _cerr = np.extract(this_grp, C_ERR[pol])
        wgt = 1./_cerr**2

        ell.append(np.mean(_ell))
        dell.append(_ell[-1]-_ell[0])
        cell.append(np.sum(_cell*wgt)/np.sum(wgt))
        dcell.append(np.sqrt(1./np.sum(wgt)))

    ell = np.array(ell)
    dell = np.array(dell)
    cell = np.array(cell)
    dcell = np.array(dcell)

    ax2.errorbar(ell, cell, xerr=dell, yerr=dcell, fmt=None, ecolor=colors[pol])
    #ax2.errorbar(ell, C2D(ell, cell), xerr=dell, yerr=C2D(ell, dcell), fmt=None, ecolor=colors[pol])

ax2.set_xlim([100,1000])
ax2.set_yscale('log')
ax2.set_xscale('log')

show()
