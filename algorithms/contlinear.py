from linear import Linear
import numpy as np
from sklearn.utils.extmath import cartesian
from configuration import *

WEIGHTS_FILE = "weightsCont.npy"

class ContLinear(Linear):

    def __init__(self, numDams, stepsize, futureDiscount, possibleActions, numNeighbors, trainTemp):
        Linear.__init__(self, numDams, stepsize, futureDiscount, possibleActions, numNeighbors, trainTemp)
        self.weights = None

    def getStateFeatures(self, state):
        (wbQIN, wbTIN, airTempForecast, solarFluxForecast, elevations, temps, time) = state

        stateVariables = []
        if self.trainTemp:
            for wb in range(self.numDams):
                for i in range(3):
                    stateVariables.append((temps[wb][i]-MIN_WATER_TEMP)/(MAX_WATER_TEMP - MIN_WATER_TEMP)) #TODO: Rescaling needed?
        else:
            for wb in range(self.numDams):
                stateVariables.append((wbQIN[wb]-MIN_QIN)/(MAX_QIN-MIN_QIN))
                stateVariables.append((elevations[wb]-MIN_ELEVATION)/(MAX_ELEVATION-MIN_ELEVATION))
            stateVariables.append((float(time)-MIN_TIME)/(MAX_TIME-MIN_TIME))

        stateFeatures = np.array(stateVariables)
        interactionTerms = np.prod(cartesian((stateVariables, stateVariables)), axis=1) # Interaction & square terms
        #TODO: Rescale interaction terms?
        stateFeatures = np.concatenate((stateFeatures, interactionTerms))
        stateFeatures = np.append(stateFeatures, 1) # Bias term
        print stateFeatures
        return stateFeatures

    def getFeatures(self, state, actionInd):
        stateFeatures = self.getStateFeatures(state)
        features = np.zeros((len(stateFeatures), self.possibleActions.shape[0]))
        features[:, actionInd] = stateFeatures
        return features


    def loadModel(self, state):
        try:
            self.weights = np.load(WEIGHTS_FILE)
            print "Restarting with existing weights"
        except IOError:
            stateFeatures = self.getStateFeatures(state)
            self.weights = np.zeros((self.numDams, stateFeatures.shape[0], self.possibleActions.shape[0]))
            print "Starting with new weights"
            print self.weights.shape
