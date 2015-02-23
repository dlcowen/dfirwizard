#setup.py for py2exe to turn live system extraction script from part 3 into a windows executable
from distutils.core import setup
import py2exe

setup(console=['dfirwizard-v3.py'])
