'''
| Filename    : config.py
| Description : Config file for keeping all the paths.
| Author      : Pushpendre Rastogi
| Created     : Fri Jan 15 19:08:08 2016 (-0500)
| Last-Updated: Fri Jan 15 19:46:35 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
_ning_dir = r'/home/hltcoe/ngao/miniScale-2016/Enron/'
flat_enron_contactgraph_fn = _ning_dir + r'contactGraph'
flat_enron_normalizecontactgraph_fn = _ning_dir + r'normalizedContactGraph'
flat_enron_query_fn = _ning_dir + r'queries'

store = r'/export/projects/prastogi/kbvn/'
optimal4randomwalk_enron_contactgraph_fn = store + r'optimal4randomwalk_enron_contactGraph.pickle'
