"""
Modern library for Linear and Integer Programming with Python 3
"""

# import into root namespace
from .src.model import *
from .src.solution import *
from .src.file_io import *
from .src.run import *
from .src.expression import *
from .src.parameter import *

# keep relative namespace
from .src import variable
from .src import solver
from .src import util

from .test import stress_test
from .test import unit_test

from .definitions import ROOT_DIR