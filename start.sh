#!/bin/bash
ALG=$1
MODE=$2
mkdir -p ../$ALG.$MODE
rsync -r * ../$ALG.$MODE
cd ../$ALG.$MODE
rm slurm*
./scripts/clear.sh
sbatch --job-name=$ALG$MODE --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu --time=300  scripts/cluster.$ALG.$MODE.sh
