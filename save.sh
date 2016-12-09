#!/bin/bash
ALG=$1
ALG="${ALG,,}"
MODE=$2
FLAGS=$3
NAME=$4
#mkdir models/$NAME
cp -Rp ../$ALG.$MODE$FLAGS models/$NAME
echo "scripts/cluster.$ALG.$MODE.sh $FLAGS" > models/$NAME/invocation
