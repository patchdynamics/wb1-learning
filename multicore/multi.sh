#!/bin/bash
ALG=$1
ALGl="${ALG,,}"
MODE=$2
FLAGS=$3
PEERS=1
#rm slurm*

#setup
for i in `seq 0 $PEERS`;
do
  echo ../multicore/$MODE.$ALGl$FLAGS$i
  mkdir -p ../multicore/$MODE.$ALGl$FLAGS$i
  rsync -r --links --exclude 'models' --exclude 'stats/*.txt' --exclude '*.npy' * ../multicore/$MODE.$ALGl$FLAGS$i
done  


RES=$(sbatch --job-name=p${ALG:0:3}${MODE:0:3} --array=0-$PEERS -p DGE multicore/invoke.$MODE.sh $ALG '0.5' $FLAGS )
RES=$(sbatch --job-name=c${ALG:0:3}${MODE:0:3} --dependency=afterok:${RES##* } -p DGE --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu  multicore/combine.weights.sh ../multicore/$MODE.$ALGl$FLAGS   $PEERS  $ALG)
anneal=(.5 .5 .5 .5 .5 .5 .5 .5 .5 .5 .5 .5 4 .4 .4 .4 .4 .4 .4 .4 .4 .4 .4 .4 .3 .3 .3 .3 .3 .3 .3 .3 .3 .3 .2 .2 .2 .2 .2 .2 .2 .2 .2 .1 .1 .1 .1 .1 .1 .1 .1 .1 .1 .1 .1 .05 .05 .05 .05 .05 .05 .05 .05 .05 )
for epsilon in "${anneal[@]}"
do
  RES=$(sbatch --job-name=p${ALG:0:3}${MODE:0:3}  --dependency=afterok:${RES##* } --array=0-$PEERS -p DGE multicore/invoke.$MODE.sh $ALG $epsilon $FLAGS )
  RES=$(sbatch --job-name=c${ALG:0:3}${MODE:0:3} --dependency=afterok:${RES##* } -p DGE --mail-type=END,FAIL  --mail-user=shultzm@stanford.edu  multicore/combine.weights.sh   ../multicore/$MODE.$ALGl$FLAGS   $PEERS  $ALG)
done

# final test run
RES=$(sbatch --job-name=f${ALG:0:3}${MODE:0:3}  --dependency=afterok:${RES##* } --array=0 -p DGE multicore/invoke.$MODE.sh $ALG $epsilon $FLAGS )
