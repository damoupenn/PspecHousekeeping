import glob

__version__ = '1.0.0'

setup_args = {
        'name': 'PspecHousekeeping',
        'author': 'David Moore',
        'author_email': 'damo@sas.upenn.edu',
        'license': 'GPL',
        'packages': ['PHK'],
        'package_dir' : {'PHK':'PHK'},
        'scripts' : glob.glob('PHK/scripts/*'),
        'version': __version__
        }

if __name__ == '__main__':
    from distutils.core import setup
    apply(setup, (), setup_args)
