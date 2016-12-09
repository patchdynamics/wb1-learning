#!/bin/bash
ALG=$1
ALG="${ALG,,}"
echo $ALG
MODE=$2
FLAGS=$3
mkdir -p ../$ALG.$MODE$FLAGS
rsync -r --links * ../$ALG.$MODE$FLAGS
cd ../$ALG.$MODE$FLAGS
rm slurm*
sbatch --job-name=$ALG$MODE --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu -p DGE  scripts/cluster.test.sh $1 $FLAGS
