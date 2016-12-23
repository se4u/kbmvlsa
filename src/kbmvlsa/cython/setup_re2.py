from distutils.core import Extension
from distutils.core import setup
from Cython.Build import cythonize

def ext(sources):
    library_dirs=['../cpp/re2/obj/so']
    return Extension(
        'thinre2',
        sources=sources,
        libraries=['re2'],
        library_dirs=library_dirs,
        include_dirs=['../cpp/re2', '../cpp/re2/re2'],
        language="c++",
        # Clang3.5 (and 3.9) seem to have a bug where the -R flag is not treated
        # properly, Moreover distutils prefixes runtime_library_dirs with L flag
        # Because of this we just pass the runtime library dirs as the rpath
        # directly on the command line.
        extra_compile_args=['-std=c++11'],
        extra_link_args=[' -rpath '+e for e in library_dirs],
    )

ext_modules = cythonize(ext(['thinre2.pyx']),)

setup(
    name='thinre2',
    version='0.1',
    description='Very thin Python wrapper for the RE2 library',
    author='Timmy Zhu; Modified by Pushpendre Rastogi',
    ext_modules=ext_modules,
)
