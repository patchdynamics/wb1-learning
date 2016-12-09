#!/bin/bash
INDEX=1
set -e
echo $INDEX
anneal=(.5 .4 .4 .3 .3 .2 .2 .1 .1 .1 .05 .05 .05 .01 .01 .01 0 0 0)
for epsilon in "${anneal[@]}"
do
  echo $INDEX
  INDEX=$epsilon
done
