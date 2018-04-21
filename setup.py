import platform
import os

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
from Cython.Build import cythonize


def scandir(dir, files=[]):
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if os.path.isfile(path) and path.endswith(".pyx"):
            files.append(path.replace(os.path.sep, ".")[:-4])
        elif os.path.isdir(path):
            scandir(path, files)
    return files


# generate an Extension object from its dotted name
def makeExtension(extName):
    fopenmp = '-fopenmp'
    if platform.system() == 'Windows':
        fopenmp = '/openmp'
    extPath = extName.replace(".", os.path.sep)+".pyx"
    return Extension(
        extName,
        [extPath],
        extra_compile_args=[fopenmp],
        extra_link_args=[fopenmp],
        )


# get the list of extensions
extNames = scandir("TokenBucket")

# and build up the set of Extension objects
extensions = [makeExtension(name) for name in extNames]

# finally, we can pass all this to distutils
setup(
  ext_modules=cythonize(extensions, build_dir="build"), install_requires=['Cython']
)

