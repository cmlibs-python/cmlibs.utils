import importlib.metadata
import sys

print("Pytho version:", sys.version)
print("importlib.metadata version:", importlib.metadata.version("importlib-metadata"))
__version__ = importlib.metadata.version("cmlibs.utils")
