#!/bin/bash
module load Python/2.7.11
export PYTHONPATH=$PYTHONPATH:/home/mshultz/virtualenvs/py2.7/lib/python2.7/
python --version
set -e
while true
do
  python runSimulation.py -e 0 --dams 1 --year 2005 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2006 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2007 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2008 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2009 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2010 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2011 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2012 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2013 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2014 -a KNN
  python runSimulation.py -e 0 --dams 1 --year 2015 -a KNN
done
