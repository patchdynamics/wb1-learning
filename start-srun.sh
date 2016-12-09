#!/bin/bash
ALG=$1
MODE=$2
mkdir -p ../$ALG.$MODE
rsync -r --links * ../$ALG.$MODE
cd ../$ALG.$MODE
rm slurm*
./scripts/clear.sh
srun -p DGE  scripts/cluster.$ALG.$MODE.sh
