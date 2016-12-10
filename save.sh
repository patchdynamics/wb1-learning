#!/bin/bash
ALG=$1
ALG="${ALG,,}"
MODE=$2
FLAGS=$3
NAME=$4
#mkdir models/$NAME
if [ -d "models/$NAME" ]; then
  echo 'dir exists'
  exit
fi
cp -Rp ../$ALG.$MODE$FLAGS models/$NAME
echo "scripts/cluster.$ALG.$MODE.sh $FLAGS" > models/$NAME/invocation
