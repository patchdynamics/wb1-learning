#!/bin/bash
ALG=$1
ALGl="${ALG,,}"
MODE=$2
FLAGS=$3
PEERS=5
rm slurm*

#setup
for i in `seq 0 $PEERS`;
do
  mkdir -p ../multicore/$MODE.$ALGl$FLAGS$i
  rsync -r --links --exclude 'models' * ../multicore/$MODE.$ALGl$FLAGS$i
done  


RES=$(sbatch --array=0-$PEERS -p DGE multicore/invoke.$MODE.sh $ALG '0.5' $FLAGS )
RES=$(sbatch --dependency=afterok:${RES##* } -p DGE --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu  multicore/combine.weights.sh ../multicore/$MODE.$ALGl$FLAGS $PEERS)
anneal=(.4 .4 .3 .3 .2 .2 .1 .1 .1 .05 .05 .05 .01 .01 .01 0 0 0)
anneal=(.4)
for epsilon in "${anneal[@]}"
do
  RES=$(sbatch --dependency=afterok:${RES##* } --array=0-$PEERS -p DGE multicore/invoke.$MODE.sh $ALG $epsilon $FLAGS )
  RES=$(sbatch --dependency=afterok:${RES##* } -p DGE --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu  multicore/combine.weights.sh ../multicore/$MODE.$ALGl$FLAGS $PEERS)
done
