import numpy as np
import aipy as a
from PspecDir import PspecDir
from capo import pspec, pfb

def sep2bl(seps, calfile='psa898_v003'):
    _seps = []
    exec('from %s import prms'%calfile)
    antpos = prms['ant_layout']
    bls = {}
    Nrow,Ncol = antpos.shape
    for ri in range(Nrow):
        for ci in range(Ncol):
            for rj in range(Nrow):
                for cj in range(ci, Ncol):
                    sep = '%d,%d' %(rj-ri, cj-ci)
                    i,j = antpos[ri,ci], antpos[rj,cj]
                    if i > j:
                        i,j = j,i
                    bls[sep] = bls.get(sep, []) + [(i,j)]
                    _seps.append(sep)
    if seps == 'all':
        seps2use = list(set(_seps))
    else:
        seps2use = seps
    rv = [','.join(['%d_%d' % (i,j) for i,j in bls[sep]]) for sep in seps2use]
    return rv

def gen_all_seps(calfile='psa898_v003'):
    seps = []
    exec('from %s import prms'%calfile)
    antpos = prms['ant_layout']
    Nrow,Ncol = antpos.shape
    for ri in range(Nrow):
        for ci in range(Ncol):
            for rj in range(Nrow):
                for cj in range(ci, Ncol):
                    seps.append('%d,%d'%(rj-ri, cj-ci))
    return seps

def gather_metadata(uv, chans, window):
    M = {}
    chans = a.scripting.parse_chans(chans, uv['nchan'])
    freqs = a.cal.get_freqs(uv['sdf'], uv['sfreq'], uv['nchan'])
    freqs = freqs.take(chans)
    M['sdf'] = uv['sdf']
    M['fq'] = np.average(freqs)
    M['z'] = pspec.f2z(M['fq'])
    M['B'] = M['sdf'] * freqs.size / pfb.NOISE_EQUIV_BW[window]
    M['etas'] = np.fft.fftshift(pspec.f2eta(freqs))
    M['kpl'] = M['etas'] * pspec.dk_deta(M['z'])
    M['bm'] = np.polyval(pspec.DEFAULT_BEAM_POLY, M['fq'])
    M['scalar'] = pspec.X2Y(M['z']) * M['bm'] * M['B']
    return chans, freqs, M

def tentothe(x):
    return map(lambda y: 10**y, x)

def P2D(kpl, kpr, p):
    return 0.5 * (kpl**2 + kpr**2)**1.5 * p / np.pi**2

def get_parent(dir_string):
    parent = dir_string
    if parent[-1] == '/':
        parent = parent[:-1]
    return parent

def uv_from_sep(sepstr, grid_spacing=[4.,32.]):
    x,y = map(lambda x: float(x), sepstr.split(','))
    return grid_spacing[0]*x, grid_spacing[1]*y

def kpr_from_sep(sepstr, fq, grid_spacing=[4.,32.]):
    kx,ky = uv_from_sep(sepstr, grid_spacing=grid_spacing)
    scalar = pspec.dk_du(pspec.f2z(fq))*(fq/0.3)
    return scalar*np.sqrt(kx**2 + ky**2)

def gather_data(parent_files, pols, seps):
    K,Pk,dPk = None,{},{}
    for i,parent in enumerate(parent_files):
        print 'Reading %d/%d: %s'%(i,len(parent_files),parent)
        D = PspecDir(parent_dir=parent)
        for parent in D.tree:
            for poldir in sorted(D.tree[parent]):
                pol = poldir.split('/')[-1]
                if not pol in pols:
                    continue
                if not pol in Pk.keys():
                    Pk[pol] = {}
                    dPk[pol] = {}
                for sepdir in D.tree[parent][poldir]:
                    sep = sepdir.split('/')[-1]
                    if not sep in seps or sep == 'all':
                        continue
                    Pfile = '%s/pspec.npz'%sepdir
                    figdata = np.load(Pfile)
                    wgt = np.abs(figdata['dPk'])**-2
                    if K is None:
                        K = figdata['Kpl']
                    try:
                        Pk[pol][i+2] += figdata['Pk'] * wgt
                        dPk[pol][i+2] += wgt
                    except(KeyError):
                        Pk[pol][i+2] = figdata['Pk'] * wgt
                        dPk[pol][i+2] = wgt
                    Pk[pol][i+2] /= dPk[pol][i+2]
                    dPk[pol][i+2] = np.sqrt(1./dPk[pol][i+2])
    return K, Pk, dPk
