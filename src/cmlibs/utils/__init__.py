import importlib.metadata
import sys

__version__ = importlib.metadata.version("cmlibs_utils" if sys.version_info < (3, 10) else "cmlibs.utils")
