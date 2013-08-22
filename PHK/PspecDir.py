import os
import datetime

def mkdir(d):
    if not os.path.exists(d):
        os.mkdir(d)
def is_empty(d):
    return os.listdir(d) == ""
def rm_if_empty(d):
    if is_empty(d):
        os.system('rm -r %d'%d)

class PspecDir(object):

    def __init__(self, parent_dir='MyPspec', timestamp=True, seps=['0,1','1,1','-1,1']):
        self.parent = parent_dir
        self.seps = seps
        if timestamp:
            ts = datetime.datetime.today()
            strfmt = '_%d-%02d-%02d_%d:%d'%(ts.year, ts.month, ts.day, ts.hour, ts.minute)
            self.parent += strfmt
        self.tree = {self.parent:{}}
        self.populate()

    def populate(self):
        mkdir(self.parent)
        for pol in 'IQUV':
            poldir = '%s/%s'%(self.parent, pol)
            self.tree[self.parent][poldir] = []
            mkdir(poldir)
            for sep in self.seps:
                sepdir = '%s/%s'%(poldir, sep)
                self.tree[self.parent][poldir].append(sepdir)
                mkdir(sepdir)

    def cleanup(self):
        for parent in D.tree:
            for poldir in D.tree[parent]:
                rm_if_empty(poldir)
                for sepdir in D.tree[parent][poldir]:
                    rm_if_empty(sepdir)
