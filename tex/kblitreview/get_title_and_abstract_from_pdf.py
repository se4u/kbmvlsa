#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
| Filename    : get_title_and_abstract_from_pdf.py
| Description : Extract the tile and abstract from a pdf file.
| Author      : Pushpendre Rastogi
| Created     : Mon Mar 21 14:29:50 2016 (-0400)
| Last-Updated: Wed Mar 23 01:56:17 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 45
'''
import sys
import rasengan
import cStringIO
import pdfminer
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from bs4 import BeautifulSoup


class Style(object):
    NUMERIC_KEYS = set(['left', 'top', 'width', 'height', 'font-size'])

    @classmethod
    def numerate(cls, k, v):
        return (k, (float(v.replace('px', ''))
                    if k in cls.NUMERIC_KEYS
                    else v))

    def __init__(self, s):
        self.s = s
        self.d = dict(self.numerate(*e.strip().split(":"))
                      for e in s.strip().split(";")
                      if e != "")

    def __getitem__(self, key):
        return self.d[key]

    def __getattr__(self, key):
        return self.d[key]

    def __repr__(self):
        return self.s


def pdfparser(data):
    fp = file(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = cStringIO.StringIO()
    device = HTMLConverter(rsrcmgr, retstr,
                           codec='utf-8',
                           laparams=pdfminer.layout.LAParams())
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    page1 = PDFPage.get_pages(fp).next()
    interpreter.process_page(page1)
    data = retstr.getvalue()
    return data


def process_soup(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    data = []
    cur_div = soup.body.div
    assert cur_div is not None
    while cur_div is not None:
        try:
            style = Style(cur_div['style'])
            span_style = Style(cur_div.span['style'])
            all_span_strings = rasengan.flatten(list(
                [list(e.stripped_strings) for e in cur_div.children]))
            data.append((style, span_style, all_span_strings))
        except:
            pass
        cur_div = cur_div.next_sibling
    return (Style(soup.span['style']), data)


def main():
    page1_html = pdfparser(args.fn)
    # Things to extract # Title, Abstract
    page_style, boxes = process_soup(page1_html)
    page_height = page_style.height
    top_boxes = [box for box in boxes if
                 box[0].top < page_height / 4]
    max_font_box_string = max(top_boxes, key=lambda x: x[1]['font-size'])[2]
    print ' '.join(max_font_box_string)
    return

if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(
        description='Get title and abstract from pdf.')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--fn', default="1403.7550v3.pdf", type=str, help='Default={"1403.7550v3.pdf"}')
    args = arg_parser.parse_args()
    import ipdb as pdb
    import traceback
    import sys
    import signal
    signal.signal(signal.SIGUSR1, lambda _sig, _frame: pdb.set_trace())
    try:
        main()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
