#!/bin/bash
./multicore/multi.sh Linear experimental temp
./multicore/multi.sh Lookup experimental temp
./multicore/multi.sh KNN experimental temp
./multicore/multi.sh Linear elevation
./multicore/multi.sh Lookup elevation
./multicore/multi.sh KNN elevation
./multicore/multi.sh KNN nolose.elevation
