#!/usr/bin/env make -f
LATEXMK := latexmk -pvc -pdf
PDFLATEXCMD := pdflatex %O -interaction=nonstopmode -synctex=1

p2: kbvntr_vanilla.pdf
p1: kbvntr.pdf 

%.pdf: %.tex
	$(LATEXMK) -pdflatex='$(PDFLATEXCMD) "\input{%S}"' $<
