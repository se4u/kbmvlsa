SHELL := /bin/bash
LATEXMK := latexmk -pvc -pdf
PDFLATEXCMD := pdflatex %O -interaction=nonstopmode -synctex=1

main: bipartitevn.tex
	$(LATEXMK) -pdflatex='$(PDFLATEXCMD) "\input{%S}"' $<
