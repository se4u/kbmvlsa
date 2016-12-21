from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import distutils.log
distutils.log.set_verbosity(distutils.log.DEBUG)

# http://stackoverflow.com/questions/18423512/
# calling-c-code-from-python-using-cython-whith-the-distutilis-approach
# echo __ZN2cv3Mat10deallocateEv) | c++filt
setup(
    name="analyzer",
    ext_modules=[
        Extension("analyzer",
                  sources=["analyzer.pyx", "KrovetzStemmer.cpp"],
                  include_dirs=["."],
                  language='c++',
                  # library_dirs=[],
                  # libraries=['python2.7'],
        ),
        Extension("xml2tabsep",
                  sources=["xml2tabsep.pyx"],
                  include_dirs=['.', '/Users/pushpendrerastogi/anaconda/lib/python2.7/site-packages/numpy/core/include'],
                  language='c++')
    ],
    cmdclass=dict(build_ext=build_ext))
