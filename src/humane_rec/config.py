import os
HOME = os.path.expanduser('~')
ACE = '%s/data/LDC2006T06/data/English.timex2norm.sgm_apf' % HOME
ACEtoWIKI = '%s/data/ACEtoWIKI_resource/ACEtoWIKI_resource.txt' % HOME


def sanitize_doc(doc):
    return doc.replace('&', 'η')


def sanitize_doc_inverse(doc):
    return doc.replace('η', '&')
