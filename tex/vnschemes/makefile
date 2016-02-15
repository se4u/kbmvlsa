LATEXMK := latexmk -pvc -pdf
PDFLATEXCMD := pdflatex %O -interaction=nonstopmode -synctex=1

main: vnschemes.tex
	$(LATEXMK) -pdflatex='$(PDFLATEXCMD) "\input{%S}"' $<
