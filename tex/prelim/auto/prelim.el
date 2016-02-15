(TeX-add-style-hook
 "prelim"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("enumitem" "shortlabels") ("glossaries" "acronym") ("xcolor" "usenames" "dvipsnames" "svgnames" "table")))
   (add-to-list 'LaTeX-verbatim-environments-local "Verbatim")
   (add-to-list 'LaTeX-verbatim-environments-local "BVerbatim")
   (add-to-list 'LaTeX-verbatim-environments-local "LVerbatim")
   (add-to-list 'LaTeX-verbatim-environments-local "SaveVerbatim")
   (add-to-list 'LaTeX-verbatim-environments-local "VerbatimOut")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "Verb")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "Verb")
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art10"
    "graphicx"
    "amsmath"
    "amssymb"
    "subcaption"
    "url"
    "xspace"
    "changepage"
    "enumitem"
    "fancyvrb"
    "glossaries"
    "xcolor"
    "todonotes")
   (TeX-add-symbols
    '("specialcell" 1)
    '("tabletodo" 1)
    '("remove" 1)
    '("note" 1)
    "eg"
    "bigeg"
    "etal"
    "etc"
    "ie"
    "bigie")
   (LaTeX-add-labels
    "sec:introduction"
    "ssec:kb"
    "sec:knowl-base-popul"
    "tab:baselines"
    "tab:lrcurve-bordes2013nips"
    "tab:metrics"
    "tab:pubs2015kbc"
    "tab:papers-classlabel"
    "sec:appendix")))

