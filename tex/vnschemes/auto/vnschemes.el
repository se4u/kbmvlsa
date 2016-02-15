(TeX-add-style-hook
 "vnschemes"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("enumitem" "shortlabels") ("glossaries" "acronym") ("bergamo" "osf")))
   (TeX-run-style-hooks
    "latex2e"
    "tufte-handout"
    "tufte-handout10"
    "graphicx"
    "amsmath"
    "amssymb"
    "url"
    "xspace"
    "enumitem"
    "fancyvrb"
    "microtype"
    "glossaries"
    "todonotes"
    "bergamo"
    "chantill")
   (TeX-add-symbols
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
    "sec:background"
    "sec:knowledge-graphs"
    "sec:communication-graphs"
    "sec:edge-for-vertex"
    "sec:experiments"
    "sec:simple-experiment")
   (LaTeX-add-bibliographies)))

