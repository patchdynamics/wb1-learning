#!/bin/bash
INDEX = 1
set -e
for epsilon in "${anneal[@]}"
do
  echo $INDEX
  INDEX=epsilon
done
