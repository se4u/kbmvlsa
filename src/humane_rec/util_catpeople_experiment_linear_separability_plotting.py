#!/usr/bin/env python
'''
| Filename    : util_catpeople_experiment_linear_separability_plotting.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Fri Sep 30 16:59:21 2016 (-0400)
| Last-Updated: Sat Oct  1 21:07:01 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 12
'''
from util_catpeople import get_pfx
import re
from catpeople_preprocessor_config import EXPCONFIG

form = lambda x: '\n'.join(r'%-7s(?P<%s_%s>[01].\d{4})'%(e, x, e.replace('@', ''))
                           for e
                           in 'AUPR RAUPR P@10 RP@10 P@100 RP@100 MRR RMRR'.split())
template = '--Train--\n%s\n--Test--\n%s'%(form('train'), form('test'))
regex = re.compile(template)
pfx = get_pfx()
lcmap = dict(logloss='red', squared_hinge='blue', blue='square_hinge', red='logloss')
def get(fn, part):
    obj = regex.match(open(fn).read())
    part = part.replace('@', '')
    return float(obj.group('%s_MRR'%part)), float(obj.group('%s_AUPR'%part))


def get_stats(ppcfg, expcfg_str='16 9 26'):
    aupr, mrr, color, C, shape = [], [], [], [], []
    for _fn, expcfg in ((pfx + '/catpeople_ls.ppcfg~%d.expcfg~%s.pkl.txt'%(ppcfg, _expcfg), _expcfg)
               for _expcfg
               in expcfg_str.split()):
        cfg = EXPCONFIG[int(expcfg)]
        c_ = cfg.lsvc_C
        loss = cfg.lsvc_loss
        if c_ > 1:
            _mrr, _aupr = get(_fn, 'test')
            color.append(lcmap[loss])
            mrr.append(_mrr)
            aupr.append(_aupr)
            C.append(c_)
            shape.append('circle')
            _mrr, _aupr = get(_fn, 'train')
            color.append('red' if loss == 'logloss' else 'blue')
            mrr.append(_mrr)
            aupr.append(_aupr)
            C.append(c_)
            shape.append('square')
    return aupr, mrr, color, C, shape

def getline2d(e):
    import matplotlib
    e = matplotlib.pyplot.Line2D([None], [None],
                                    color="white",
                                    markerfacecolor=e.get_facecolor(),
                                    marker=('o'
                                            if isinstance(e, matplotlib.pyplot.Circle)
                                             else 's'),
                                    markevery=[0],
                                    clip_box=matplotlib.transforms.Bbox([[0, 0], [0, 0]]),
                                    clip_on=True,
                                    visible=True)
    return e
