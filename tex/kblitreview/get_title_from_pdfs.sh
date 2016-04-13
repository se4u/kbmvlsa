for f in pdfdir/*.pdf
do
    printf "$f "
    ./get_title_and_abstract_from_pdf.py --fn "$f"
done
