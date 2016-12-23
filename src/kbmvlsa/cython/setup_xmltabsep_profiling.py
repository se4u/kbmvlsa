#-- Put this at the start of setup.py --#
# import os
# os.environ.setdefault('DISTUTILS_DEBUG', failobj='1')
# import distutils.log
# distutils.log.set_verbosity(distutils.log.DEBUG)
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy
# http://stackoverflow.com/questions/18423512/
# calling-c-code-from-python-using-cython-whith-the-distutilis-approach
# echo __ZN2cv3Mat10deallocateEv) | c++filt
# define_macros = [('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')]
define_macros = []
define_macros = [('CYTHON_TRACE', 1)]
compiler_directives = dict(embedsignature=True,
                           boundscheck=False,
                           initializedcheck=False,
                           profile=True,
                           linetrace=True,
                           binding=True
)
setup(ext_modules=cythonize(
          Extension("xml2tabsep",
                    sources=["xml2tabsep.pyx", "KrovetzStemmer.cpp"],
                    include_dirs=['.', numpy.get_include()],
                    define_macros=define_macros,
                    language='c++'),
          compiler_directives=compiler_directives),
      cmdclass=dict(build_ext=build_ext))
