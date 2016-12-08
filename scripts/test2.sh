#!/bin/bash
./scripts/clear.sh
echo '.'
./runSimulation.py  --year 2005 --test > /dev/null
echo '.'
./runSimulation.py  --year 2006 --test > /dev/null
echo '.'
./runSimulation.py  --year 2007 --test > /dev/null
echo '.'
./runSimulation.py  --year 2008 --test > /dev/null
echo '.'
./runSimulation.py  --year 2009 --test > /dev/null
