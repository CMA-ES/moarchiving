# from distutils.core import setup
from setuptools import setup
import warnings
from moarchiving import __version__
from moarchiving import __doc__ as long_description

# prevent the error when building Windows .exe
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
    codecs.register(func)

# packages = ['cma'],  # indicates a multi-file module and that we have a cma folder and cma/__init__.py file

try:
    with open('README.md') as file_:
        long_description = file_.read()  # now assign long_description=long_description below
except IOError:  # file not found
    warnings.warn("README.md file not found")
    # long_description = ""
else:
    long_description = long_description.split("## Testing")[0]
    with open('README.txt', 'w') as file_:
        file_.write(long_description)

setup(name="moarchiving",
      long_description=long_description,  # __doc__, # can be used in the cma.py file
      long_description_content_type='text/markdown',
      version=__version__.split()[0],
      description="Biobjective Archive class with hypervolume indicator "
                  "and uncrowded hypervolume improvement computation "
                  "",
      author="Nikolaus Hansen",
      author_email="authors_firstname.lastname@inria.fr",
      # maintainer="Nikolaus Hansen",
      # maintainer_email="authors_firstname.lastname@inria.fr",
      url="https://github.com/cma-es/moarchiving",
      license="BSD",
      classifiers = [
          "Intended Audience :: Science/Research",
          "Intended Audience :: Education",
          "Intended Audience :: Other Audience",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Mathematics",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved :: BSD License",
      ],
      keywords=["optimization", "multi-objective",],
      packages=["moarchiving"],
      # install_requires=["bisect"],
      extras_require={
            "arbitrary-precision": ["fraction"],
      },
      package_data={'': ['LICENSE', ]},  # i.e. moarchiving/LICENSE
      )
