#!/usr/bin/python
import sys, getopt
import os
sys.path.append(os.getcwd())
import numpy as np
import subprocess
from shutil import copyfile
import struct
from sklearn.utils.extmath import cartesian
import random
import re
import importlib
from algorithms.linear import Linear

CONTROL_DIR = "./"
TOKENIZED_CON_FILE = "w2_con_tokenized.npt"
CON_FILE = "w2_con.npt"
TEMPERATURE_FILE = "spr.opt"
QWO_FILE = "qwo_34.opt"
QOUT_FILE = "qot_br1.npt"
RSI_FILE = "rso%STEP%.opt"
CHAINING_FILE = CONTROL_DIR + "scripts/propagate.flow.sh"
ELEVATION_FILE = "wl.opt"
STATS_DIR = "stats/"
REWARDS_FILE = "rewards.txt"
ACTIONS_FILE = "actions.txt"
QIN_FILE = "QINs.txt"
TIN_FILE = "TINs.txt"

# Hyperparameters
EPSILON_GREEDY = 0.1 # TODO: Should start high & decrease over time
FUTURE_DISCOUNT = 0.95
STEP_SIZE = 0.1

# Actions
# Simple for elevation training
SPILLWAY_OUTFLOWS = [0]
POWERHOUSE_OUTFLOWS = [300, 500, 700, 900, 1100, 1300, 1500, 1700, 1900, 2100, 2300, 2500, 2700, 2900, 3100, 3300, 3500, 3700, 3900, 4100, 4500, 5000, 5500, 6000]
HYPOLIMNAL_OUTFLOWS = [0]
# Three way
#POWERHOUSE_OUTFLOWS = [300, 500, 700, 900, 1100, 1300, 1500, 1700, 1900, 2101, 2300, 2500, 2700, 2900, 3100, 3300, 3500]
#SPILLWAY_OUTFLOWS = [0, 300, 500, 700, 900, 1100, 1300, 1500, 1700, 1900, 2101, 2300, 2500, 2700, 2900, 3100, 3300, 3500]
#HYPOLIMNAL_OUTFLOWS = [0, 300, 500, 700, 900, 1100, 1300, 1500, 1700, 1900, 2101, 2300, 2500, 2700, 2900, 3100, 3300, 3500]

NUM_ALLOWED_ACTIONS = 12
# Reward parameters
TARGET_ELEVATION = 227.5

# Actions for Temperature training
#GATE_OPTIONS = np.array(["Spill", "Power", "Hypo", "Spill-Power", "Hypo-Power"])
GATE_OPTIONS = np.matrix('1, 0, 0; 0, 1, 0; 0, 0, 1; 0.5, 0.5, 0; 0, 0.5, 0.5')

# Set to true to stop learning
TESTING = False
# Randomize inputs to explore the state space (mixnmatch)
RANDOMIZE = False
# Train temperature (false to train elevation)
TRAIN_TEMP = False

def modifyControlFile(fileDir, timeStart, timeEnd, year):
    with open(fileDir + CON_FILE, "w") as fout:
        with open(fileDir + "inputs/control/" + TOKENIZED_CON_FILE, "r") as fin:
            for line in fin:
                line = line.replace("%RSIFN%", RSI_FILE.replace("%STEP%", str(timeStart)))
                line = line.replace("%TMSTRT%", str(timeStart).rjust(8))
                line = line.replace("%TMEND_%", str(timeEnd).rjust(8))
                line = line.replace("%YEAR__%", str(year).rjust(8))
                fout.write(line)

def setAction(fileDir, currentTime, action, wb):
    line = str(currentTime+1).rjust(8)
    line += str(action[0]).rjust(8)
    line += str(action[1]).rjust(8)
    line += str(action[2]).rjust(8)
    line += "\n"
    with open(fileDir + QOUT_FILE, "a") as f:
        f.write(line)

def getReward(wb, currentTime):
    wlFile = CONTROL_DIR + "wb" + str(wb+1) + "/" + ELEVATION_FILE
    elevations = np.genfromtxt(wlFile, delimiter=",")
    elevation = elevations[-1,33]

    if TRAIN_TEMP:
        wbiTIN= np.loadtxt('wb1/tin.npt', skiprows=3)
        tempIn = wbiTIN[np.where(wbiTIN[:,0]==currentTime),1]
        print "TEMP IN", tempIn

        temperatureOut = np.loadtxt( "wb" + str(wb+1) + "/two_34.opt", skiprows=3)
        temperatureOut = temperatureOut[-1,1]
        reward = (tempIn - temperatureOut - 100) # Always negative reward to encourage exploration
    else:
        #reward = (MAX_ELEVATION - TARGET_ELEVATION - 1) - (elevation - TARGET_ELEVATION)**2
        reward = 50 - abs(elevation - TARGET_ELEVATION)
        #if elevation < MIN_ELEVATION or elevation > MAX_ELEVATION:
        #    reward = -100

    return reward, elevation

def copyInInputFiles(year, numDams, randomize=False):
    for wb in range(1, numDams + 1):
        wbDir = CONTROL_DIR + "wb" + str(wb) + "/"
        copyfile( wbDir + "inputs/met" + str(year) +".npt", CONTROL_DIR + "wb" + str(wb) + "/met.npt")
	copyfile( wbDir + "inputs/QOUT" + str(year) +".npt", wbDir + "qot_br1.npt" )
        #subprocess.check_call(['./scripts/copy.qout.sh', '93', str(year)  ], shell=True)

    copyfile( CONTROL_DIR + "wb1/inputs/QIN" + str(year) +".npt", CONTROL_DIR + "wb1/qin.npt")
    copyfile( CONTROL_DIR + "wb1/inputs/TIN" + str(year) +".npt", CONTROL_DIR + "wb1/tin.npt")
    # here we could randomize the temperature input files if we like
    if(randomize):
        randyear = random.randint(2005,2015)
        copyfile( CONTROL_DIR + "wb1/inputs/TIN" + str(randyear) +".npt", CONTROL_DIR + "wb1/tin.npt")
        print 'rand mixnmatch ' + str(randyear)

def copyInOutputFiles(year, numDams):
    for wb in range(1, numDams + 1):
        wbDir = CONTROL_DIR + "wb" + str(wb) + "/"
        spinupDir =  wbDir + "inputs/spinup/" + str(year) + "/"
        files = os.listdir(wbDir)
        for file in files:
            if file.endswith(".opt"):
                os.remove(os.path.join(wbDir,file))
        copyfile( spinupDir + "wl.opt", wbDir + "wl.opt" )
        copyfile( spinupDir + "spr.opt", wbDir + "spr.opt" )

def calculatePossibleActions():
    if TRAIN_TEMP:
        return np.array(GATE_OPTIONS)
    return cartesian((SPILLWAY_OUTFLOWS, POWERHOUSE_OUTFLOWS, HYPOLIMNAL_OUTFLOWS))

# returns state represented as a tuple of (QINs, TINs, airTempForecast, solarFluxForecast, elevations, temps, time)
def getState(currentTime, year, actionInds, numActions):
    wbQIN = np.empty(numDams)
    wbTIN = np.empty(numDams)

    # Get QIN/TIN for today on Dam 1
    wbiQIN= np.loadtxt('wb1/qin.npt', skiprows=3)
    wbQIN[0] = wbiQIN[np.where(wbiQIN[:,0]==currentTime),1]
    wbiTIN= np.loadtxt('wb1/tin.npt', skiprows=3)
    wbTIN[0] = wbiTIN[np.where(wbiTIN[:,0]==currentTime),1]

    # Read last QIN/TIN for each of Dams 2-4
    for f in range(2, numDams+1):
        wbiQIN = np.loadtxt('wb'+str(f)+'/qin.npt', skiprows=3)
        wbQIN[f-1] = wbiQIN[np.where(wbiQIN[:,0]==currentTime),1]
        wbiTIN = np.loadtxt('wb'+str(f)+'/tin.npt', skiprows=3)
        wbTIN[f-1] = wbiTIN[np.where(wbiTIN[:,0]==currentTime),1]

    # Weather Judgement
    # Read in next week of weather
    # Average and noise it
    # this is a 'fake forecast'
    # Note: Using the same meteorological data for all dams
    futureDays = 5
    met = np.loadtxt('wb1/met.npt', skiprows=3, delimiter=',')
    future = met[np.where(np.logical_and(met[:,0] >= currentTime, met[:,0] < currentTime+futureDays))]
    average = sum(future)/futureDays
    airTempForecast = np.random.normal(average[1], scale=2)
    solarFluxForecast = np.random.normal(average[6], scale=50)

    elevations = np.zeros(numDams)
    temps = np.zeros([numDams,3])
    for f in range(1, numDams+1):
        # Water Level
        wlFile = CONTROL_DIR + "wb" + str(f) + "/" + ELEVATION_FILE
        wbElevations = np.genfromtxt(wlFile, delimiter=",")
        elevations[f-1] = wbElevations[-1,33]

        # Output Structure +/- 65 F / 16 C
        if TRAIN_TEMP:
            seg34 = np.loadtxt('wb'+str(f)+'/spr.opt', skiprows=3, usecols=[1,4])
            seg34ForTime = seg34[np.where(np.floor(seg34[:,0]) == currentTime)]
            temp220 = float(seg34ForTime[seg34ForTime[:,0].size - 15,1])
            temp202 = float(seg34ForTime[seg34ForTime[:,0].size - 11,1])
            temp191 = float(seg34ForTime[seg34ForTime[:,0].size - 6,1])
            #temp220 = 0
            #temp202 = 0
            #temp191 = 0
            temps[f-1] = [temp220, temp202, temp191]

    #gateState = np.zeros((numDams, numActions)) #numDams x numActions
    #for i in range(numDams):
    #    gateState[i, actionInds.astype(int)[i]] = 1
    # stateArray = np.append(stateArray, gateState.flatten())

    return (wbQIN, wbTIN, airTempForecast, solarFluxForecast, elevations, temps, currentTime)

def getAction(state, dam, possibleActions, currentTime):
    (wbQIN, wbTIN, airTempForecast, solarFluxForecast, elevations, temps, stateTime) = state
    if TRAIN_TEMP:
        print 'TEMP'
        numActions = len(possibleActions)
        allowedActions = range(numActions)
    else:
        print 'ELEV'
        numActions = NUM_ALLOWED_ACTIONS
        actionQOUT = np.sum(possibleActions, 1)
        # Only allow actions that are within NUM_ALLOWED_ACTIONS of to QIN
        distances = (actionQOUT - wbQIN) ** 2
        allowedActions = np.argpartition(distances, numActions)[:numActions]
    #print(possibleAction[allowedActions])
    #print(np.sum(possibleActions[allowedActions],1))

    if not TESTING and random.random() < (EPSILON_GREEDY - .5 * (numDays-(currentTime-90))/float(numDays)):
        print 'Random'
        print (numDays-(currentTime-90))/float(numDays)
        print EPSILON_GREEDY - .5 * (numDays-(currentTime-90))/float(numDays)
        chosenAction = random.randrange( numActions )
        return allowedActions[chosenAction]
    else:
        [bestActionInd, Vopt] = algorithm.getBestAction(state, dam)
        return bestActionInd

def outputStats(rewards, elevations, wbQIN, wbTIN, actionInds, possibleActions):
    with open(STATS_DIR + REWARDS_FILE, "a") as fout:
        np.savetxt(fout, rewards, newline=",")
        np.savetxt(fout, elevations, newline=",")
        fout.write("\n")
    with open(STATS_DIR + ACTIONS_FILE, "a") as fout:
        for i in range(numDams):
            action = possibleActions[actionInds[i]]
            #_print action, sum(int(flow) for flow in action)
            np.savetxt(fout, action, fmt="%1f",newline=",")
        fout.write("\n")
    with open(STATS_DIR + QIN_FILE, "a") as fout:
        np.savetxt(fout, wbQIN, newline=",")
        fout.write("\n")
    with open(STATS_DIR + TIN_FILE, "a") as fout:
        np.savetxt(fout, wbTIN, newline=",")
        fout.write("\n")
    for i in range(numDams):
        temperatureOut = np.loadtxt( "wb" + str(i+1) + "/two_34.opt", skiprows=3)
        temperatureOut = temperatureOut[-1,1]
        tempFile = STATS_DIR + "temperatures" + str(i+1) +".txt"
        with open(tempFile, "a") as fout:
            np.savetxt(fout, [temperatureOut], newline=",")
            fout.write("\n")
    algorithm.outputStats(STATS_DIR)

timeStart = 1
currentTimeBegin = 90
timeStep = 1
year = 2015
numDams = 1
numDays = 220 - currentTimeBegin
repeat = 1
algClass = getattr(importlib.import_module("algorithms.linear"), "Linear")

if len(sys.argv) > 1:
    try:
      opts, args = getopt.getopt(sys.argv[1:],"ha:e:r:d:ts:",["eps=", "alg=", "repeat=", "dams=", "days=", "test", "year=", "step=", "rand", "temp"])
    except getopt.GetoptError:
      print 'runSimulation.py -a <algorithm> -r <repeat> -e <epsilon> -d <dams>, days=<days> -s <stepsize> --test --rand'
      sys.exit()

    for opt, arg in opts:
      if opt == '-h':
         #_#_print 'runSimulation.py -r <repeat> -e <epsilon> -d <numDams>, --days <numDays> -s <stepsize> --test'
         sys.exit()
      elif opt in ("-e", "--eps"):
         EPSILON_GREEDY = float(arg)
      elif opt in ("-s, --step"):
         STEP_SIZE = float(arg)
      elif opt in ("-r", "--repeat"):
         repeat = int(arg)
      elif opt in ("-d", "--dams"):
         numDams = int(arg)
      elif opt in ("--days"):
         numDays = int(arg)
      elif opt in ("--year"):
         year = int(arg)
      elif opt in ("-t", "--test"):
          TESTING = True
      elif opt in ("--rand"):
          RANDOMIZE = True
      elif opt in ("-a", "--alg"):
          algClass = getattr(importlib.import_module("algorithms."+arg.lower()), arg)
      elif opt in ("--temp"):
          TRAIN_TEMP = True

possibleActions = calculatePossibleActions()
print possibleActions
algorithm = algClass(numDams, STEP_SIZE, FUTURE_DISCOUNT, possibleActions, NUM_ALLOWED_ACTIONS, TRAIN_TEMP)
for r in range(repeat):
    currentTime = currentTimeBegin
    if(RANDOMIZE):
        year = random.randint(2005,2015)
        print 'rand year' + str(year)
    copyInInputFiles(year, numDams, RANDOMIZE)
    copyInOutputFiles(year, numDams)
    state = getState(currentTime, year, np.ones(numDams)*4, possibleActions.shape[0])

    algorithm.loadModel(state)

    actionInds = np.zeros(numDams)
    rewards = np.zeros(numDams)
    elevations = np.zeros(numDams)
    for i in range(numDays):
        print 'Day ' + str(currentTime)
        copyInOutputFiles(year, numDams)
        for wb in range(numDams):
            actionInd = getAction(state, wb, possibleActions, currentTime)
            actionInds[wb] = actionInd
            action = possibleActions[actionInd]
            (wbQIN, wbTIN, airTempForecast, solarFluxForecast, elevationVals, temps, stateTime) = state
            if TRAIN_TEMP:
                action = np.multiply(action, wbQIN) # TODO: Make this the output from elevation training instead
                print 'action', action

            wbDir = 'wb'+str(wb+1)+'/'
            ##_print wbDir
            modifyControlFile(wbDir, timeStart, currentTime + timeStep, year)
            setAction(wbDir, currentTime, action, wb)
            path = os.getcwd()
            os.chdir(wbDir)
            #subprocess.check_call(['/home/mshultz/ror-dam-simulation/bin/cequalw2.v371.linux', '.'], shell=True)
            subprocess.check_call(['../bin/cequal', '.'], shell=True)
            os.chdir(path)
            if wb != (numDams - 1):
                subprocess.check_call([CHAINING_FILE, "wb" + str(wb+1), "wb" + str(wb+2)])

            rewards[wb], elevations[wb] = getReward(wb, currentTime)
            #raw_input("Press Enter to continue...")
        #print rewards
        #if True in ( rewards <= -1000): # Game over
        #    nextState = None
        #else:
        nextState = getState(currentTime + timeStep, year, actionInds, possibleActions.shape[0])
        #print nextState
        if not TESTING:
            algorithm.incorporateObservations(state, actionInds, rewards, nextState)
        #print 'done with observations'
        outputStats(rewards, elevations, wbQIN, wbTIN, actionInds, possibleActions)
        if not nextState:
            # Game over, move to next epoch
            print 'Day ' + str(currentTime)
            print 'Lose'
            print state
            print elevations[0]
            print possibleActions[actionInds[0]]
            print np.sum(possibleActions[actionInds[0]])
            print rewards[0]
            with open(STATS_DIR + 'lastday.txt', "a") as fout:
                 np.savetxt(fout, [currentTime], newline=",")
                 fout.write("\n")
            algorithm.saveModel()
            sys.exit()

        currentTime = currentTime + timeStep
        state = nextState



    algorithm.saveModel()
    with open(STATS_DIR + 'lastday.txt', "a") as fout:
         np.savetxt(fout, [currentTime], newline=",")
         fout.write("\n")
