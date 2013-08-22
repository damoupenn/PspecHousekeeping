import os
import datetime

def mkdir(d):
    if not os.path.exists(d):
        os.mkdir(d)

class PspecDir(object):
    def __init__(self, parent_dir='MyPspec', timestamp=True):
        self.parent = parent_dir
        if timestamp:
            ts = datetime.datetime.today()
            strfmt = '%d-%02d-%02d_%d%d'%(ts.year, ts.month, ts.day, ts.hour, ts.minute)
            self.parent += strfmt
            self.populate()
    def populate(self):
        mkdir(self.parent)
        for pol in 'IQUV':
            poldir = '%s/%s'%(self.parent, pol)
            mkdir(poldir)
