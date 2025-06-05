import importlib.metadata
import sys

print("Python version:", sys.version)
try:
    print("importlib.metadata version:", importlib.metadata.version("importlib.metadata"))
except:
    pass
try:
    print("importlib-metadata version:", importlib.metadata.version("importlib-metadata"))
except:
    pass
try:
    print("importlib_metadata version:", importlib.metadata.version("importlib_metadata"))
except:
    pass
__version__ = importlib.metadata.version("cmlibs.utils")
