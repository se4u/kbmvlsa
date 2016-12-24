
def main(debug=False, define_macros=None, extra_directives=None,
         extension_ns=(("xml2tabsep", ("xml2tabsep.pyx",)),
                       ("analyzer", ("analyzer.pyx", "KrovetzStemmer.cpp")))):
    if debug:
        import os
        os.environ.setdefault('DISTUTILS_DEBUG', failobj='1')
        import distutils.log
        distutils.log.set_verbosity(distutils.log.DEBUG)
        pass
    from distutils.core import setup
    from distutils.extension import Extension
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize
    import numpy
    define_macros = ([]
                     if define_macros is None
                     else list(define_macros))
    compiler_directives = dict(embedsignature=True,
                               boundscheck=False,
                               initializedcheck=False)
    if extra_directives is not None:
        compiler_directives.update(extra_directives)
    include_dirs = ['.', numpy.get_include()]
    extensions = [Extension(a, sources=list(b), include_dirs=include_dirs,
                            define_macros=define_macros, language='c++')
                  for (a,b)
                  in extension_ns]
    setup(ext_modules=cythonize(extensions,
                                nthreads=2,
                                language='c++',
                                compiler_directives=compiler_directives),
          cmdclass=dict(build_ext=build_ext))
    return

if __name__ == '__main__':
    main()
