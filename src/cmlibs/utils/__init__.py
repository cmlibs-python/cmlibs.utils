import importlib.metadata
import sys

print("Python version:", sys.version)
xx = ('', 'X.Y.Z')
try:
    xx = ("importlib.metadata version:", importlib.metadata.version("importlib.metadata"))
except:
    pass
try:
    xx = ("importlib-metadata version:", importlib.metadata.version("importlib-metadata"))
except:
    pass
try:
    xx = ("importlib_metadata version:", importlib.metadata.version("importlib_metadata"))
except:
    pass
print(xx)
__version__ = importlib.metadata.version("cmlibs.utils")
