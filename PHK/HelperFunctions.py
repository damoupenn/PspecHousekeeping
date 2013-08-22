def sep2bl(seps, calfile='psa898_v003'):
    exec('from %s import prms'%calfile)
    antpos = prms['antpos']
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
    rv = [','.join(['%d_%d' % (i,j) for i,j in bls[sep]]) for sep in seps]
    return rv
