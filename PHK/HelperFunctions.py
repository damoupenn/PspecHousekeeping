import numpy as np
from capo import pspec

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

