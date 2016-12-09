#!/bin/bash
ALG=$1
MODE=$2
FLAGS=$3
mkdir -p ../$ALG.$MODE$FLAGS
rsync -r --links * ../$ALG.$MODE$FLAGS
cd ../$ALG.$MODE$FLAGS
rm slurm*
./scripts/clear.sh
sbatch --job-name=$ALG$MODE --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu -p DGE  scripts/cluster.$ALG.$MODE.sh $FLAGS
