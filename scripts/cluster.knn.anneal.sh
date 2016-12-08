#!/bin/bash
module load Python/2.7.11
export PYTHONPATH=$PYTHONPATH:/home/mshultz/virtualenvs/py2.7/lib/python2.7/
python --version
echo $anneal
set -e
for epsilon in $anneal
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
