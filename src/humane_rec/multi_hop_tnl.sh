#!/usr/bin/env bash
PORT=${1-13579}
ssh prastog3@login.clsp.jhu.edu nc -z localhost 13579
if [[ $? == 1 ]]
then
    echo \# -------------------------------------- \#
    echo   Setting up connection from CLSP -> r6n23
    echo \# -------------------------------------- \#
    CMD="ssh -f -T prastog3@login.clsp.jhu.edu autossh -M 13580 -N  -T -L${PORT}:r6n23:${PORT} prastogi@test1.hltcoe.jhu.edu"
    $CMD
fi
echo Testing connection from CLSP to r6n23 via test1
[[ $(ssh prastog3@login.clsp.jhu.edu curl localhost:${PORT}/Q2Fy) == Q2FyDQoxCUNhcglfCU5PVU4JTk4JXwkwCVJPT1QJXwlf ]] || exit 1

nc -z localhost $PORT
if [[ $? == 1 ]]
then
    echo \# -------------------------------------- \#
    echo   Setting up connection from Local to CLSP
    echo \# -------------------------------------- \#
    CMD="autossh -M 13581 -f -N -T -L${PORT}:localhost:${PORT} prastog3@login.clsp.jhu.edu"
    $CMD
fi
echo Testing connection from local machine to r6n23
[[ $(curl localhost:${PORT}/Q2Fy) == Q2FyDQoxCUNhcglfCU5PVU4JTk4JXwkwCVJPT1QJXwlf ]] || exit 1


