#!/usr/bin/env python
'''
| Filename    : create_igraph_from_flatfile.py
| Description : Create an Igraph Object from the flatfile format that Ning provided.
| Author      : Pushpendre Rastogi
| Created     : Thu Jan 14 15:59:54 2016 (-0500)
| Last-Updated: Thu Jan 14 18:15:48 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 40

The flatfile format used by Ning and Doug is lexically sorted and it has an
attribute of edge strength. The lexical sorting itself is not a problem since
we have the "guarantee" (that we assert) that there are no gaps in the integral
node names.

'''
import rasengan
import os
import igraph

def read_file(fn):
    data = []
    with rasengan.tictoc("Disk Read"):
        raw_data = open(fn).read()
    with rasengan.tictoc("Data Processing"):
        for e in raw_data.strip().split('\n'):
            e = e.strip().split()
            data.append([int(e[0]), int(e[1]), float(e[2])])
    return data

def main():
    with rasengan.tictoc("Reading Data"):
        data = read_file(args.fn)
    v_left = [e[0] for e in data]
    v_right = [e[1] for e in data]
    node_names = sorted(list(set(v_left + v_right)))
    # The total nodes in contactGraph were 111,932
    print 'Total nodes=', len(node_names)
    #-----------------------------------------------------------------------#
    # Test for gaps revealed that the flatfile contains gaps in node names. #
    # So we need to map the node names to something contiguous.             #
    #-----------------------------------------------------------------------#
    igraph_node_to_flatfile_map = dict(enumerate(node_names))
    flatfile_to_igraph_node_map = dict((e, i) for (i, e) in enumerate(node_names))
    with open(os.path.join(args.outdir, out_fn + '_flatfile_to_igraph_node_map'), 'wb') as ofh:
        for flatnode, igraphnode in flatfile_to_igraph_node_map.iteritems():
            ofh.write('%d %d\n'%(flatnode, igraphnode))

    with rasengan.tictoc("Creating Graph"):
        g = igraph.Graph()
        g.add_vertices(len(node_names))
        g.add_edges(
            [(flatfile_to_igraph_node_map[a], flatfile_to_igraph_node_map[b])
             for (a,b,_) in data])
        g.es["weights"] = [weight for (_, __, weight) in data]
        pass
    outfn = os.path.join(args.outdir, args.outfn)
    assert '.' not in outfn
    for format in ['graphml', 'dot', 'ncol']:
        with rasengan.tictoc('Writing Format='+format):
            with open(outfn + '.' + format, 'wb') as ofh:
                g.write(ofh, format=format)
    return

if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='Igraph Creator')
    arg_parser.add_argument(
        '--fn', default='/home/hltcoe/ngao/miniScale-2016/Enron/contactGraph',
        type=str)
    arg_parser.add_argument(
        '--outdir', default='/export/projects/prastogi/kbvn/', type=str)
    arg_parser.add_argument('--outfn', default='enron_contactgraph', type=str)
    # It takes 84.6 s to read the plaintext file on COE.
    # But only 0.1 s for the disk read. Everthing else is consumed by the string
    # handling so remove that bottleneck.
    arg_parser.add_argument('--plaintext', default=1, type=int,
                            help=('Should the file be interpreted as plaintext?'
                                  ' Default={1}'))
    args=arg_parser.parse_args()
    main()
