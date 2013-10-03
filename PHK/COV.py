import numpy as np

def cov(m):
    X = np.array(m, ndmin=2, dtype=np.complex)
    X -= X.mean(axis=1)[(slice(None),np.newaxis)]
    N = X.shape[1]
    fact = float(N-1)
    return (np.dot(X, X.T.conj()) / fact).squeeze()

class COV:
    def __init__(self, Tk, gp1, gp2, niter=1):
        self.bls = gp1+gp2
        self.gp1 = gp1
        self.gp2 = gp2
        self.X = Tk
        self.niter = niter
        self.Nbl = len(self.bls)
        self.Nk = Tk.shape[0]/len(self.bls)
        self.N = len(Tk)
        self.C = cov(Tk)
        self.inds = np.arange(self.N)
        self.Ctot = 1
        self.Pk = []

    def get_T(self,bl):
        i = self.bls.index(bl)
        return self.X[i*self.Nk:(i+1)*self.Nk].copy()

    def normalize_cov(self, ARP=True): #why not normalize in both directions?
        d = np.diag(self.C)
        _n = len(d)
        d.shape = (1,_n)
        self.C /= np.sqrt(d)*2
        if not ARP:
            d.shape = (_n,1)
            self.C /= 0.5*np.sqrt(d)

    def zero_diags(self):
        for b in range(self.Nbl):
            indb = self.inds[:-b*self.Nk]
            self.C[indb, indb+b*self.Nk] = self.C[indb+b*self.Nk, indb] = 0.
        self.C[self.inds,self.inds] = 0.

    def remove_common_cov(self):
        self.C.shape = (self.Nbl, self.Nk, self.Nbl, self.Nk)
        self.Csum = np.zeros_like(self.C)
        for i in xrange(self.Nbl):
            bli = self.bls[i]
            for j in xrange(self.Nbl):
                Sum, Wgt = 0,0
                blj = self.bls[j]
                if bli in self.gp1 and blj in self.gp1:
                    gp = self.gp1
                elif bli in self.gp2 and blj in self.gp2:
                    gp = self.gp2
                else:
                    continue
                for bli_ in gp:
                    i_ = self.bls.index(bli_)
                    if i == i_:
                        continue
                    for blj_ in gp:
                        j_ = self.bls.index(blj_)
                        if j == j_:
                            continue
                        Sum += self.C[i_,:,j_,:]
                        Wgt += 1
                self.Csum[i,:,j,:] = Sum/Wgt
        self.C.shape = self.Csum.shape = (self.Nbl*self.Nk, self.Nbl*self.Nk)
        self.C -= self.Csum

    def mask_intragroup_pairings(self):
        mask = np.ones_like(self.C)
        for bl1 in xrange(len(self.gp1)):
            for bl2 in xrange(len(self.gp2)):
                bl2 += len(self.gp1)
                mask[bl1*self.Nk: (bl1+1)*self.Nk, bl2*self.Nk:(bl2+1)*self.Nk] = 0
                mask[bl2*self.Nk: (bl2+1)*self.Nk, bl1*self.Nk:(bl1+1)*self.Nk] = 0
        self.C *= mask

    def approx_inv(self, gain=1.):
        self.C *= -gain
        self.C[self.inds, self.inds] = 1.
        self.X = np.dot(self.C, self.X)

    def gen_pspecs(self):
        P = []
        for i, bl1 in enumerate(self.bls):
            for bl2 in self.bls[i+1:]:
                x1 = self.get_T(bl1)
                x2 = self.get_T(bl2)
                P.append(np.mean(x1 * np.conj(x2), axis=-1))
        return P
