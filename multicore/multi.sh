#!/bin/bash
ALG=$1
ALG="${ALG,,}"
MODE=$2
FLAGS=$3
PEERS=5
#rm slurm*

#setup
for i in `seq 0 $PEERS`;
do
  mkdir -p ../multicore/$ALG.$MODE$FLAGS$i
  rsync -r --links --exclude 'models' * ../multicore/$ALG.$MODE$FLAGS$i
done  


echo $INDEX > status.log
RES=$(sbatch --array=1-$PEERS -p DGE ./wait.sh)
#RES=$(sbatch --dependency=afterok:${RES##* } -p DGE combine.weights.sh)
#$INDEX = $((INDEX + 1))
#RES=$(sbatch --array=1-$PEERS -p DGE ./wait.sh)
#RES=$(sbatch --dependency=afterok:${RES##* } -p DGE combine.weights.sh)
