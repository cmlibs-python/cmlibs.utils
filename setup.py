from setuptools import setup, find_packages
import io

# List all of your Python package dependencies in the
# requirements.txt file

def readfile(filename, split=False):
    with io.open(filename, encoding="utf-8") as stream:
        if split:
            return stream.read().split("\n")
        return stream.read()

readme = readfile("README.rst", split=True)[3:]  # skip title
requires = readfile("requirements.txt", split=True)
licence = readfile("LICENSE")

setup(
    name='opencmiss.utils',
    version='0.1.0',
    description='OpenCMISS Utilities for Python.',
    long_description='\n'.join(readme) + licence,
    classifiers=[],
    author='Hugh Sorby',
    author_email='',
    url='',
    license='APACHE',
    packages=find_packages(exclude=['ez_setup',]),
    namespace_packages=['opencmiss'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)

