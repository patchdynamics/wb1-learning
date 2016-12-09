#!/bin/bash
ALG=$1
FLAG=$2
MODE='experimental'
cd /home/mshultz/learning/wb1-learning/multicore/$MODE.$ALG$FLAG$i
module load Python/2.7.11
export PYTHONPATH=$PYTHONPATH:/home/mshultz/virtualenvs/py2.7/lib/python2.7/
python --version
set -e
TASK=$SLURM_ARRAY_TASK_ID
if [ $TASK -eq 0 ]
then
  python runSimulation.py -e 0 --dams 1 --year 2015 -a $ALG $FLAG --test #> /dev/null
else
  python runSimulation.py -e $epsilon --dams 1 --year 2015 -a $ALG $FLAG #> /dev/null
fi

