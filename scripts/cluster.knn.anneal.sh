#!/bin/bash
module load Python/2.7.11
export PYTHONPATH=$PYTHONPATH:/home/mshultz/virtualenvs/py2.7/lib/python2.7/
python --version
anneal=(.5 .4 .4 .3 .3 .2 .2 .1 .1 .1 .05 .05 .05 .01 .01 .01 0 0 0)
set -e
for epsilon in "${anneal[@]}"
do
	for n in $(seq 25)
	do
		echo $n	
		echo $epsilon
		python runSimulation.py -e $epsilon --dams 1 --year 2005 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2006 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2007 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2008 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2009 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2010 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2011 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2012 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2013 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2014 -a KNN #> /dev/null
		python runSimulation.py -e $epsilon --dams 1 --year 2015 -a KNN #> /dev/null
	done
done
