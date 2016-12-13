from linear import Linear
import numpy as np
from sklearn.utils.extmath import cartesian

WEIGHTS_FILE = "weightsCont.npy"
QIN_MIN = 400
QIN_MAX = 7000
ELEVATION_MIN = 220
ELEVATION_MAX = 235
TEMP_MIN = 4
TEMP_MAX = 22
TIME_MIN = 1
TIME_MAX = 365

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
                    stateVariables.append((temps[wb][i]-TEMP_MIN)/(TEMP_MAX - TEMP_MIN)) #TODO: Rescaling needed?
        else:
            for wb in range(self.numDams):
                stateVariables.append((wbQIN[wb]-QIN_MIN)/(QIN_MAX-QIN_MIN))
                stateVariables.append((elevations[wb]-ELEVATION_MIN)/(ELEVATION_MAX-ELEVATION_MIN))
            stateVariables.append((float(time)-TIME_MIN)/(TIME_MAX-TIME_MIN))

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
