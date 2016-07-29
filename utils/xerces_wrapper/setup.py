import distutils 
from distutils.core import setup, Extension 

setup(
    name = "Wrapper of C++ Xerces Library for python",
    author = 'Guillaume SOUSA AMARAL',
    author_email = 'guillaume.sousa@nist.gov',
    version = "0.1",
    ext_modules = [
        Extension(
            "_xerces_wrapper",
            sources = ["xerces_wrapper.i", "xerces_wrapper.cxx"],
            swig_opts = ["-c++"],
			libraries = ["xerces-c"],
			library_dirs=["path/to/xerces/src"], #Win: C://path//to//xerces//src
			include_dirs =["path/to/xerces/src"]
            )
        ]
    )
	