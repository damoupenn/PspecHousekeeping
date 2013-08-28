import os
import datetime

def is_empty(d):
    return len(os.listdir(d)) == 0
def rm_if_empty(d):
    if is_empty(d):
        os.system('rm -r %s'%d)
def mkdir(d):
    if not os.path.exists(d):
        os.mkdir(d)
def ls(d):
    return os.listdir(d)

class PspecDir(object):

    def __init__(self, parent_dir='MyPspec', timestamp=True, seps=['0,1','1,1','-1,1'], new=True):
        self.parent = parent_dir
        self.seps = seps
        if timestamp:
            ts = datetime.datetime.today()
            strfmt = '_%d-%02d-%02d_%d:%d'%(ts.year, ts.month, ts.day, ts.hour, ts.minute)
            self.parent += strfmt
        self.tree = {self.parent:{}}
        self.new = new
        self.populate()

    def populate(self):
        if self.new:
            self._populate_new()
        else:
            self._populate_old()

    def _populate_new(self):
        mkdir(self.parent)
        for pol in 'IQUV':
            poldir = '%s/%s'%(self.parent, pol)
            self.tree[self.parent][poldir] = []
            mkdir(poldir)
            for sep in self.seps:
                sepdir = '%s/%s'%(poldir, sep)
                self.tree[self.parent][poldir].append(sepdir)
                mkdir(sepdir)

    def _populate_old(self):
        for poldir in map(lambda x: '%s/%s'%(self.parent, x), ls(self.parent)):
            self.tree[self.parent][poldir] = []
            for sepdir in map(lambda x: '%s/%s'%(poldir, x), ls(poldir)):
                self.tree[self.parent][poldir].append(sepdir)

    def cleanup(self):
        for parent in self.tree:
            for poldir in self.tree[parent]:
                rm_if_empty(poldir)
                for sepdir in self.tree[parent][poldir]:
                    rm_if_empty(sepdir)
        self.tree = {self.parent:{}}
        self._populate_old()
