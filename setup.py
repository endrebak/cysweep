from distutils.core import setup

from setuptools import find_packages, Extension, Command
from Cython.Build import cythonize

extensions = [Extension("chromsweep.src.chromsweep",
                        ["chromsweep/src/chromsweep.pyx"], language="c++")]

setup(ext_modules = cythonize(extensions))
