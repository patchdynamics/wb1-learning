#!/bin/bash
module load Python/2.7.11
export PYTHONPATH=$PYTHONPATH:/home/mshultz/virtualenvs/py2.7/lib/python2.7/
python --version

python runSimulation.py -e 1 --dams 1 --year 2015 -a $1 $2 #> /dev/null
python runSimulation.py -e 0 --dams 1 --year 2015 -a $1 $2 --test #> /dev/null


