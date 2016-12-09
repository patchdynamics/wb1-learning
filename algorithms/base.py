import numpy as np
import random

class Base():

    def __init__(self, numDams, stepsize, futureDiscount, possibleActions, numAllowedActions, trainTemp):
        self.numDams = numDams
        self.stepsize = stepsize
        self.futureDiscount = futureDiscount
        self.possibleActions = possibleActions
        self.numAllowedActions = numAllowedActions
        self.trainTemp = trainTemp

    ######### Required Methods ############

    def getQopt(self, state, actionInd, dam):
        raise NotImplementedError()

    def incorporateObservations(self, state, actionInds, rewards, nextState):
        raise NotImplementedError()



    ########## Optional Methods ###########

    def outputStats(self, statsDir):
        pass

    def saveModel(self):
        pass

    def loadModel(self, state):
        pass


    ########## Common Methods ############


    def getBestAction(self, state, dam):
        #print 'getBestAction'
        (wbQIN, wbTIN, airTempForecast, solarFluxForecast, elevations, temps) = state

        if self.trainTemp:
            numActions = len(self.possibleActions)
            allowedActions = range(numActions)
        else:
            actionQOUT = np.sum(self.possibleActions, 1)
            distances = (actionQOUT - wbQIN) ** 2
            allowedActions = np.argpartition(distances, self.numAllowedActions)[:self.numAllowedActions]

        Qopts = np.empty(self.possibleActions.shape[0])
        Qopts.fill(-float("inf"))
        for actionInd in allowedActions:
            Qopts[actionInd] = self.getQopt(state, actionInd, dam)
        #_print 'Qopts'
        #print Qopts
        #Qopts[disallowedActions] = -float("inf")
        bestActionIndices = np.argwhere(Qopts == np.max(Qopts))
        #print 'best action ind'
        #print np.max(Qopts)
        #print bestActionIndices
        bestActionInd = random.choice(bestActionIndices)[0] # Make sure not always choosing first action if all valued same
        return bestActionInd, Qopts[bestActionInd]

    def discretizeState(self, state):
        (wbQIN, wbTIN, airTempForecast, solarFluxForecast, elevations, temps) = state

        wbQINindicators = np.empty([self.numDams,8])
        wbTINindicators = np.empty([self.numDams,6])
        for f in range(0, self.numDams):
            wbQINindicators[f,0] = int(wbQIN[f] <= 700)
            wbQINindicators[f,1] = int(wbQIN[f] > 700  and wbQIN[f] <= 1200)
            wbQINindicators[f,2] = int(wbQIN[f] > 1200  and wbQIN[f] <= 1700)
            wbQINindicators[f,3] = int(wbQIN[f] > 1700  and wbQIN[f] <= 2200)
            wbQINindicators[f,4] = int(wbQIN[f] > 2200  and wbQIN[f] <= 2700)
            wbQINindicators[f,5] = int(wbQIN[f] > 2700  and wbQIN[f] <= 3200)
            wbQINindicators[f,6] = int(wbQIN[f] > 3700  and wbQIN[f] <= 4200)
            wbQINindicators[f,7] = int(wbQIN[f] > 4200)
            wbTINindicators[f,0] = int(wbTIN[f] <= 12)
            wbTINindicators[f,1] = int(wbTIN[f] > 12 and wbTIN[f] <= 14)
            wbTINindicators[f,2] = int(wbTIN[f] > 14 and wbTIN[f] <= 16)
            wbTINindicators[f,3] = int(wbTIN[f] > 16 and wbTIN[f] <= 18)
            wbTINindicators[f,4] = int(wbTIN[f] > 18 and wbTIN[f] <= 20)
            wbTINindicators[f,5] = int(wbTIN[f] > 20)
        ##_print(wbQINindicators)
        ##_print(wbTINindicators)

        weatherJudgements = np.empty([self.numDams,2])
        airTempJudgement = int(airTempForecast > 18.3)
        solarFluxJudgement = int(solarFluxForecast > 300)
        weatherJudgements[f-1] = [airTempJudgement, solarFluxJudgement]

        elevationStep = 1
        elevationLevels = range(215, 241, elevationStep)
        elevationJudgements = np.zeros([self.numDams,len(elevationLevels)+2])
        for wb in range(self.numDams):
            lesser = np.array(elevationLevels) < elevations[wb]
            greater = np.array(elevationLevels) >= elevations[wb]-elevationStep
            if(np.sum(lesser) == 1):
                elevationJudgements[wb][:-2] = lesser.astype(int)
            elif(np.sum(greater) == 1):
                elevationJudgements[wb][:-2] = greater.astype(int)
            else:
                elevationJudgements[wb][:-2] = np.logical_and(lesser, greater).astype(int)
            if elevationLevels[0] >= elevations[wb]:
                elevationJudgements[-2] = 1
            elif elevationLevels[-1] < elevations[wb]-elevationStep:
                elevationJudgements[-1] = 1
            if(np.sum(elevationJudgements[wb]) != 1):
                print elevations[wb]
                print lesser
                print greater
                print elevationJudgements
                print 'ERROR'
                raw_input("Press Enter to continue...")
            ##_print 'Elevation Judgements'
            ##_print elevation
            #_print elevationJudgements

        tempStep = 0.5
        tempLevels = np.arange(4, 22, tempStep)
        temperatureJudgements = np.zeros([self.numDams, 3, len(tempLevels)+2])
        for wb in range(self.numDams):
            for i in range(3):
                lesser = np.array(tempLevels) < temps[wb][i]
                greater = np.array(tempLevels) >= temps[wb][i]-tempStep
                if(np.sum(lesser) == 1):
                    temperatureJudgements[wb][i][:-2] = lesser.astype(int)
                elif(np.sum(greater) == 1):
                    temperatureJudgements[wb][i][:-2] = greater.astype(int)
                else:
                    temperatureJudgements[wb][i][:-2] = np.logical_and(lesser, greater).astype(int)
                if tempLevels[0] >= temps[wb][i]:
                    temperatureJudgements[-2] = 1
                elif tempLevels[-1] < temps[wb][i]-tempStep:
                    temperatureJudgements[-1] = 1
                if(np.sum(temperatureJudgements[wb][i]) != 1):
                    print temperatureJudgements[wb]
                    print lesser
                    print greater
                    print temperatureJudgements
                    print 'ERROR'
                    raw_input("Press Enter to continue...")


        # Construct State Array
        if self.trainTemp:
            stateArray = (temperatureJudgements.flatten())
            #stateArray = np.append(stateArray, weatherJudgements[0,0])
            #stateArray = np.append(stateArray, wbTINindicators)
        else:
            stateArray = elevationJudgements.flatten()
            stateArray = np.append(stateArray, wbQINindicators)

        return stateArray
