#!/usr/bin/env python
import sys
mode = sys.argv[1]
del sys.argv[1]
statfn = "/tmp/Profile.prof"
if mode == "line":
    import line_profiler
    from xml2tabsep import main, parse_args
    profile = line_profiler.LineProfiler(main)
    profile.runcall(main, parse_args())
    assert len(profile.get_stats().timings) > 0, "No profile stats."
    profile.dump_stats(statfn)
    profile.print_stats()
else:
    import cProfile, pstats
    cProfile.runctx('from xml2tabsep import *; args=parse_args(); dict_list=main(args)', globals(), locals(), "/tmp/Profile.prof")
    stats = pstats.Stats(statfn)
    stats.strip_dirs().sort_stats("time").print_stats(20)
