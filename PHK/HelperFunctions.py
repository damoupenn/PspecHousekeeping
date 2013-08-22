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
