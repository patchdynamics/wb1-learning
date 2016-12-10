#!/bin/bash
ALG=$1
ALGl="${ALG,,}"
FLAG=$3
EPSILON=$2
MODE='experimental'
TASK=$SLURM_ARRAY_TASK_ID
cd /home/mshultz/learning/multicore/$MODE.$ALGl$FLAG$TASK
echo /home/mshultz/learning/multicore/$MODE.$ALGl$FLAG$TASK
module load Python/2.7.11
export PYTHONPATH=$PYTHONPATH:/home/mshultz/virtualenvs/py2.7/lib/python2.7/
python --version
set -e
if [ $TASK -eq 0 ]
then
  echo "python runSimulation.py -e 0 --dams 1 --year 2015 -a $ALG --$FLAG --test #> /dev/null"
  python runSimulation.py -e 0 --dams 1 --year 2015 -a $ALG --$FLAG --test #> /dev/null
else
  echo $EPSILON
  echo "python runSimulation.py -e $EPSILON --dams 1 --year 2015 -a $ALG --$FLAG #> /dev/null"
  python runSimulation.py -e $EPSILON --dams 1 --year 2015 -a $ALG --$FLAG #> /dev/null
fi

