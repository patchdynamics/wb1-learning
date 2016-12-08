#!/bin/bash
ALG=$1
MODE=$2
mkdir -p ../$ALG
rsync -r * ../$ALG
cd ../$ALG
rm slurm*
./scripts/clear.sh
sbatch --job-name=THING --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu --time=300  scripts/run.$ALG.$MODE.cluster.sh
