from setup import main
define_macros = [('CYTHON_TRACE', 1)]
extra_directives= dict(profile=True,
                       linetrace=True,
                       binding=True)
if __name__ == '__main__':
    main(define_macros=define_macros, extra_directives=extra_directives)
