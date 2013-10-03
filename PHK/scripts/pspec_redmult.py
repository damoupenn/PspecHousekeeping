#! /usr/bin/env python

import aipy as a
import numpy as np
import capo
import optparse
import sys
import os
import PHK
from pylab import *

o = optparse.OptionParser()
a.scripting.add_standard_options(o, ant=True, pol=True, chan=True)
o.add_option('-n','--nboot', dest='nboot', default=10, type=int,
        help='number of bootstraps')
opts,args = o.parse_args(sys.argv[1:])

PLOT = True
WINDOW = 'blackman-harris'

uv = a.miriad.UV(args[0])
chans, freqs, M = PHK.gather_metadata(uv, opts.chan, WINDOW)
del(uv)

T = {}
N = {}
times = []

def gen_noise_spec(chans,nchan):
    Tsys = 560e3
    B = 100e6 / nchan
    Nday = 20.
    Nbl = 4.
    Npol = 2.
    t_int = 43.
    noise = np.random.normal(size=chans.size) * np.exp(2j*np.pi*np.random.uniform(size=chans.size))
    return noise / np.sqrt(B*t_int*Nday*Nbl*Npol)

Jy2mK = capo.pspec.jy2T(freqs)
for uvfile in args:
    uvi = a.miriad.UV(uvfile)
    a.scripting.uv_selector(uvi, opts.ant, opts.pol)
    for (uvw, t, bl),d,f in uvi.all(raw=True):
        if not t in times:
            times.append(t)
        #gather data
        d = d.take(chans)
        f = f.take(chans)
        w = np.logical_not(f).astype(np.float)
        w *= a.dsp.gen_window(uvi['nchan'], WINDOW).take(chans)
        Trms = d * Jy2mK
        Nrms = w * gen_noise_spec(chans, uvi['nchan'])

        #this is the delay transform
        window = a.dsp.gen_window(Trms.size, WINDOW)
        Trms = np.fft.ifft(window*Trms)
        Nrms = np.fft.ifft(window*Trms)
        Wrms = np.fft.ifft(w)

        if np.abs(Wrms[0]) > 0: #only if you have data...
            #invert what window function there is.
            Trms.shape = (Trms.size, 1)
            Nrms.shape = (Nrms.size, 1)
            C = np.zeros((Trms.size, Trms.size), dtype=np.complex)
            for k1 in xrange(Wrms.size):
                for k2 in xrange(Wrms.size):
                    C[k1,k2] = Wrms[k1-k2]
            Cinv = np.linalg.inv(C)
            Trms = np.fft.fftshift(np.dot(Cinv, Trms).squeeze())
            Nrms = np.fft.fftshift(np.dot(Cinv, Nrms).squeeze())

        T[bl] = T.get(bl, []) + [Trms]
        N[bl] = N.get(bl, []) + [Nrms]

Nk = chans.size
bls = T.keys()
Nbl = len(bls)

for bl in bls:
    T[bl] = np.array(T[bl])
    N[bl] = np.array(N[bl])

def bootstrap_bls(bls, Nboot):
    if Nboot == 1:
        gp1, gp2 = bls[:Nbl/2], bls[Nbl/2:]
        return gp1, gp2, gp1+gp2
    else:
        import random
        _bls = random.sample(bls, len(bls))
        gp1, gp2 = _bls[:Nbl/2], _bls[Nbl/2:]
        for _gp in [gp1,gp2]:
            try:
                _gp = random.sample(_gp, 2) + [random.choice(_gp) for bl in _gp[:len(_gp)-2]]
            except(ValueError):
                pass
        return gp1, gp2, gp1 + gp2

for boot in xrange(opts.nboot):
    gp1, gp2, _bls = bootstrap_bls(bls, opts.nboot)

    for X in [T,N]:
        Xs = np.concatenate([X[bl] for bl in _bls], axis=-1).T
        CX_tot = 1

        Cx = PHK.COV(Xs, gp1, gp2)

        for iter in range(5):

            Cx = PHK.COV(Xs, gp1, gp2)
            Cx.normalize_cov(ARP=False)
            Cx.zero_diags()
            Cx.remove_common_cov()
            Cx.mask_intragroup_pairings()
            Cx.approx_inv(gain=0.3)

            Xs = Cx.X
            CX_tot = np.dot(Cx.C, CX_tot)

        Xs = np.concatenate([X[bl] for bl in _bls], axis=-1).T
        Xs = np.dot(CX_tot, Xs)
        Cx = PHK.COV(Xs, gp1, gp2)

        show()
