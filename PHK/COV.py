def cov(m):
    X = np.array(m, ndmin=2, dtype=np.complex)
    X -= X.mean(axis=1)[(slice(None),np.newaxis)]
    N = X.shape[1]
    fact = float(N-1)
    return (np.dot(X, X.T.conj()) / fact).squeeze()

class COV:
    def __init__(self, Tk, bls, gain=1):
        self.bls = bls
        self.X = Tk
        self.gain = gain
        self.Nbl = len(bls)
        self.Nk = Tk.shape[0]/len(bls)
        self.N = len(Tk)
        self.C = cov(Tk)
        self.inds = np.arange(self.N)
        self.Ctot = 1
        self.Pk = []
    def get_T(self,bl):
        i = self.bls.index(bl)
        return self.X[i*self.Nk:(i+1)*self.Nk].copy()
    def normalize_cov(self): #why not normalize in both directions?
        norm = np.diag(self.C)
        for i,var in enumerate(norm):
            self.C[i,:] /= np.sqrt(2.*var)
            self.C[:,i] /= np.sqrt(2.*var)
        #norm.shape = (1, len(norm))
        #self.C /= np.sqrt(norm)*2.
    def zero_diags(self):
        for b in range(self.Nbl):
            indb = self.inds[:-b*self.Nk]
            self.C[indb, indb+b*self.Nk] = self.C[indb+b*self.Nk, indb] = 0.
        self.C[self.inds,self.inds] = 0.
    def remove_common_cov(self):
        self.C.shape = (self.Nbl, self.Nk, self.Nbl, self.Nk)
        self.Cavg = np.zeros_like(self.C)
        for i in xrange(self.Nbl):
            for j in xrange(self.Nbl):
                not_ij = np.array([bl for bl in xrange(self.Nbl) if not bl in (i,j)])
                avg_Nij = self.C.take(not_ij, axis=0).take(not_ij, axis=2)
                avg_Nij = np.mean(np.mean(avg_Nij, axis=2), axis=0)
                self.Cavg[i,:,j,:] = avg_Nij
        self.C.shape = self.Cavg.shape = (self.Nbl*self.Nk, self.Nbl*self.Nk)
        self.C -= self.Cavg
    def subtract_cov(self):
        self.C *= -self.gain
        self.C[self.inds, self.inds] = 1.
        self.X = np.dot(self.C, self.X)
        self.Ctot = np.dot(self.C, self.Ctot)
    def gen_pspecs(self):
        P = []
        for i, bl1 in enumerate(self.bls):
            for bl2 in self.bls[i+1:]:
                x1 = self.get_T(bl1)
                x2 = self.get_T(bl2)
                P.append(np.mean(x1 * np.conj(x2), axis=-1))
        return P
